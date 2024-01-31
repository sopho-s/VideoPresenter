
from PyQt5.QtWidgets import *
import sys
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from threading import *
import pickle



class VideoEditor(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyQt5 Media Player")
        self.setGeometry(350, 100, 700, 500)

        p =self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)

        self.init_ui()

        self.flags = []

        self.show()


    def init_ui(self):

        #create media player object
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)


        #create videowidget object

        videowidget = QVideoWidget()


        #create open button
        openBtn = QPushButton('Open Video')
        openBtn.clicked.connect(self.open_file)



        #create button for playing
        self.playBtn = QPushButton()
        self.playBtn.setEnabled(False)
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.clicked.connect(self.play_video)



        #create slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0,0)
        self.slider.sliderMoved.connect(self.set_position)



        #create label
        self.label = QLabel()
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)


        #create hbox layout
        hboxLayout = QHBoxLayout()
        hboxLayout.setContentsMargins(0,0,0,0)

        #set widgets to the hbox layout
        hboxLayout.addWidget(openBtn)
        hboxLayout.addWidget(self.playBtn)
        hboxLayout.addWidget(self.slider)


        self.flagBtn = QPushButton("Flag")
        self.flagBtn.clicked.connect(self.flag)
        self.saveBtn = QPushButton("Save")
        self.saveBtn.clicked.connect(self.save)

        editorlayout = QHBoxLayout()
        editorlayout.addWidget(self.flagBtn)
        editorlayout.addWidget(self.saveBtn)

        #create vbox layout
        vboxLayout = QVBoxLayout()
        vboxLayout.addLayout(editorlayout)
        vboxLayout.addWidget(videowidget)
        vboxLayout.addLayout(hboxLayout)
        vboxLayout.addWidget(self.label)


        self.setLayout(vboxLayout)

        self.mediaPlayer.setVideoOutput(videowidget)


        #media player signals

        self.mediaPlayer.stateChanged.connect(self.mediastate_changed)
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)


    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")
        self.filename = filename

        if filename != '':
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
            self.playBtn.setEnabled(True)


    def play_video(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()

        else:
            self.mediaPlayer.play()


    def mediastate_changed(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playBtn.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause)

            )

        else:
            self.playBtn.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay)

            )

    def position_changed(self, position):
        self.slider.setValue(position)


    def duration_changed(self, duration):
        self.slider.setRange(0, duration)


    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    def flag(self):
        self.flags.append(self.mediaPlayer.position())
        print(self.flags)

    def save(self):
        with open('flags.flg', 'wb') as f:
            pickle.dump(sorted(self.flags), f)
        self.close()

    def handle_errors(self):
        self.playBtn.setEnabled(False)
        self.label.setText("Error: " + self.mediaPlayer.errorString())


class VideoPlayer(QWidget):
    def __init__(self, video, flag):
        super().__init__()

        self.setWindowTitle("PyQt5 Media Player")
        self.setGeometry(350, 100, 700, 500)

        p =self.palette()
        p.setColor(QPalette.Window, Qt.black)
        self.setPalette(p)

        self.init_ui()

        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(video)))
        self.showFullScreen()
        self.setCursor(Qt.BlankCursor) 


        with open(flag, 'rb') as f:
            self.flags = pickle.load(f)
        self.nextflagindex = 0
        self.flag = 0
        self.show()


    def init_ui(self):

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        videowidget = QVideoWidget()

        vboxLayout = QVBoxLayout()
        vboxLayout.addWidget(videowidget)


        self.setLayout(vboxLayout)

        self.mediaPlayer.setVideoOutput(videowidget)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pressPos = event.pos()
            print(self.flags)

    def mouseReleaseEvent(self, event):
        if (self.pressPos is not None and
            event.button() == Qt.LeftButton and
            event.pos() in self.rect()) :
            if len(self.flags) > self.nextflagindex:
                self.flag = self.flags[self.nextflagindex]
                self.nextflagindex += 1
                self.mediaPlayer.play()
                self.animation=Thread(target=self.animate)
                self.animation.start()
            else:
                self.mediaPlayer.play()
        self.pressPos = None

    def animate(self):
        while True:
            pos = self.mediaPlayer.position()
            if pos > self.flag:
                self.mediaPlayer.pause()
                break





class MenuWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Presentation")
        Select = QPushButton("Edit")
        Select.clicked.connect(self.Selected)
        Play = QPushButton("Play")
        Play.clicked.connect(self.Play)
        hbox = QHBoxLayout()
        hbox.addWidget(Select)
        hbox.addWidget(Play)
        widget = QWidget()
        widget.setLayout(hbox)
        self.setCentralWidget(widget)

    def Selected(self):
        self.mediaplayer = VideoEditor()

    def Play(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")
        self.filename = filename

        if filename != '':
            filename, _ = QFileDialog.getOpenFileName(self, "Open Flag")
            self.mediaplayer = VideoPlayer(self.filename, filename)


app = QApplication(sys.argv)

window = MenuWindow()
window.show()


sys.exit(app.exec_())