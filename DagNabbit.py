import logging
import traceback
import nuke, hiero
import time
import os
import sys
from PySide2 import QtWidgets, QtOpenGL, QtGui, QtCore
from PySide2.QtWidgets import QApplication
from math import ceil
from typing import Tuple

def getDagWidget() -> QtOpenGL.QGLWidget:
	"""Retrieve the QGLWidget of DAG graph"""
	stack = QtWidgets.QApplication.topLevelWidgets()
	while stack:
		widget = stack.pop()
		if widget.objectName() == 'DAG.1':
			for c in widget.children():
				if isinstance(c, QtOpenGL.QGLWidget):
					return c

		stack.extend(c for c in widget.children() if c.isWidgetType())


def grabDagFramebuffer(dag: QtOpenGL.QGLWidget, painter: QtGui.QPainter, xpos: int, ypos: int) -> None:
	"""Draw dag frame buffer to painter image at given coordinates"""
	# updateGL does some funky stuff because grabFrameBuffer grabs the wrong thing without it
	dag.updateGL()
	pix = dag.grabFrameBuffer()
	painter.drawImage(xpos, ypos, pix)


class DagWrapper():
	"""Wrapper for Nuke DAG"""
	def __init__(
			self,
			dag: QtOpenGL.QGLWidget=None,
			selectedNodes: []=nuke.selectedNodes(),
			allNodes: []=nuke.allNodes(),
			zoom: float = 1.0,
			margins: int = 100
	) -> None:
		super(DagWrapper, self).__init__()
		self.dag = getDagWidget()
		self.selectedNodes = selectedNodes
		self.allNodes = allNodes
		self.zoom = zoom
		self.margins = margins


	def bboxAllNodes(self) -> Tuple[int, int, int, int]:
		"""Calculate the total size of the DAG"""
		minX, minY, maxX, maxY = [], [], [], []
		for node in self.allNodes:
			minX.append(node.xpos())
			minY.append(node.ypos())
			maxX.append(node.xpos() + node.screenWidth())
			maxY.append(node.ypos() + node.screenHeight())
		return (min(minX), min(minY), max(maxX), max(maxY))

	def bboxSelectedNodes(self) -> Tuple[int, int, int, int]:
		"""Calculate the selected nodes size of the DAG"""
		minX, minY, maxX, maxY = [], [], [], []
		if len(self.selectedNodes) > 0:
			for node in self.selectedNodes:
				minX.append(node.xpos())
				minY.append(node.ypos())
				maxX.append(node.xpos() + node.screenWidth())
				maxY.append(node.ypos() + node.screenHeight())
			return (min(minX), min(minY), max(maxX), max(maxY))
		else:
			return self.bboxAllNodes()

	def size(self, margins=100, zoom=1.0, selectedNodesOnly=False) -> QtCore.QSize:
		"""Calculate the size of DAG for given zoom and margins"""
		bbox = self.bboxAllNodes()
		if selectedNodesOnly: bbox = self.bboxSelectedNodes()

		minX, minY, maxX, maxY = bbox
		minX -= int(margins / zoom)
		minY -= int(margins / zoom)
		maxX += int(margins / zoom)
		maxY += int(margins / zoom)

		width = (int((maxX - minX) * zoom))
		height = (int((maxY - minY) * zoom))

		return QtCore.QSize(width,height)

	def sizeForAllNodes(self) -> QtCore.QSize:
		return self.size(margins=self.margins, zoom=self.zoom, selectedNodesOnly=False)

	def sizeForSelectedNodes(self) -> QtCore.QSize:
		return self.size(margins=self.margins, zoom=self.zoom, selectedNodesOnly=True)

	def centerForAllNodes(self) -> QtCore.QPoint:
		"""Return center for all nodes"""
		margins=self.margins
		zoom=self.zoom
		minX, minY, maxX, maxY = self.bboxAllNodes()
		width = int(maxX - minX)
		height = int(maxY - minY)
		centerX = int(maxX - (width/2))
		centerY = int(maxY - (height/2))
		return QtCore.QPoint(centerX,centerY)

	def centerForSelectedNodes(self) -> QtCore.QPoint:
		"""Return center for selected nodes"""
		margins=self.margins
		zoom=self.zoom
		minX, minY, maxX, maxY = self.bboxSelectedNodes()
		width = int(maxX - minX)
		height = int(maxY - minY)
		centerX = int(maxX - (width/2))
		centerY = int(maxY - (height/2))
		return QtCore.QPoint(centerX,centerY)

class ResetWorkspaceWorker(QtCore.QRunnable):
	"""
	Executes code in a seperate thread.
	Communicates with the ThreadPool it spawned from via signals.
	"""
	StatusOk = 0
	StatusError = 1

	def __init__(
			self,
			workspace: str = 'Compositing',
		) -> None:
			logging.info("ResetWorkspaceWorker Class init")
			super(ResetWorkspaceWorker, self).__init__()
			self.signals = ThreadSignals()
			self.workspace = workspace

	def run(self):
		logging.info("ResetWorkspaceWorker Run")
		status = ResetWorkspaceWorker.StatusOk

		try:
			nuke.executeInMainThreadWithResult(self.resetWorkspace, ())

		except Exception as e:
			logging.info (traceback.format_exc())
			status = ResetWorkspaceWorker.StatusError

		self.signals.finished.emit(status)
		self.signals.stringSignal.emit("ResetWorkspaceWorker Finished")

	def resetWorkspace(self):
		hiero.ui.setWorkspace(self.workspace)
		hiero.ui.resetCurrentWorkspace()


class PrepareDagWorker(QtCore.QRunnable):
	"""
	Executes code in a seperate thread.
	Communicates with the ThreadPool it spawned from via signals.
	"""
	StatusOk = 0
	StatusError = 1

	def __init__(
			self,
			dagWrapper: DagWrapper,
			workspace: str = 'Compositing',
			fitDagToSelectedNodes: bool = False,
			zoom: float = 1.0,
			margins: int = 100,
			delay: float = 1.0,
			selectedNodes: []=nuke.selectedNodes(),
			highlightNodes: bool = False
		) -> None:
			logging.info("PrepareDagWorker Class init")
			super(PrepareDagWorker, self).__init__()
			self.signals = ThreadSignals()
			self.dagWrapper = dagWrapper
			self.workspace = workspace
			self.fitDagToSelectedNodes = fitDagToSelectedNodes
			self.zoom = zoom
			self.margins = margins
			self.delay = delay
			self.selectedNodes = selectedNodes
			self.highlightNodes = highlightNodes

	def run(self):
		logging.info("PrepareDagWorker Run")
		status = PrepareDagWorker.StatusOk

		try:
			nuke.executeInMainThreadWithResult(self.prepareDag, ())

		except Exception as e:
			logging.info (traceback.format_exc())
			status = PrepareDagWorker.StatusError

		self.signals.finished.emit(status)
		self.signals.stringSignal.emit("PrepareDagWorker Finished")

	def prepareDag(self):
		self.resizeDag()
		self.selectNodes()

	def resizeDag(self):
		if hiero.ui.currentWorkspace != self.workspace:
			hiero.ui.setWorkspace(self.workspace)
			hiero.ui.resetCurrentWorkspace()

		# Push window partially offscreen
		# A partially offscreen window will allowed to be bigger than the screen
		imageSize = self.dagWrapper.sizeForAllNodes()
		imageCenter = self.dagWrapper.centerForAllNodes()

		if self.fitDagToSelectedNodes:
			imageSize = self.dagWrapper.sizeForSelectedNodes()
			imageCenter = self.dagWrapper.centerForSelectedNodes()

		dagWindow = self.dagWrapper.dag.window()
		logging.info("Resizing Dag to output size %s, %s" % (imageSize.width(), imageSize.height()))
		dagWindow.hide()
		dagWindow.setWindowFlags(dagWindow.windowFlags() | QtCore.Qt.X11BypassWindowManagerHint)
		dagWindow.resize(imageSize.width(),imageSize.height())
		dagWindow.move(200,200)
		self.dagWrapper.dag.resize(imageSize.width(),imageSize.height())
		nuke.zoom (self.zoom, (imageCenter.x(),imageCenter.y()))
		time.sleep(self.delay)
		dagWindow.show()

	def selectNodes(self):
		for node in self.dagWrapper.allNodes:
			node['selected'].setValue(False)

		if self.highlightNodes:
			if len(self.selectedNodes) > 0:
				for node in self.selectedNodes:
					node['selected'].setValue(True)
			else:
				for node in self.dagWrapper.allNodes:
					node['selected'].setValue(True)



class CaptureDagWorker(QtCore.QRunnable):
	"""
	Executes code in a seperate thread.
	Communicates with the ThreadPool it spawned from via signals.
	"""
	StatusOk = 0
	StatusError = 1

	def __init__(
			self,
			dagWrapper: DagWrapper,
			imagePath: str = '/tmp/DagNabbit.png',
			nodeInfoPath: str = '/tmp/DagNabbit.info',
			delay: float = 1.0,
			highlightNodes: bool = False
		) -> None:
			logging.info("PrepareDagWorker Class init")
			super(CaptureDagWorker, self).__init__()
			self.signals = ThreadSignals()
			self.imagePath = imagePath
			self.nodeInfoPath = nodeInfoPath
			self.dagWrapper = dagWrapper
			self.delay = delay

	def run(self):
		logging.info("CaptureDagWorker Run")
		status = CaptureDagWorker.StatusOk

		try:
			nuke.executeInMainThreadWithResult(self.captureDag, ())

		except Exception as e:
			logging.info (traceback.format_exc())
			status = CaptureDagWorker.StatusError

		self.signals.finished.emit(status)
		self.signals.stringSignal.emit("CaptureDagWorker Finished")

	def captureDag(self):
		# Create a pixmap to store the results
		time.sleep(self.delay)
		pixmap = QtGui.QPixmap(self.dagWrapper.dag.width(), self.dagWrapper.dag.height())
		painter = QtGui.QPainter(pixmap)
		painter.setCompositionMode(painter.CompositionMode_SourceOver)
		grabDagFramebuffer(self.dagWrapper.dag, painter, 0, 0)
		painter.end()

		path = os.path.expanduser(self.imagePath)
		saveSuccessful = pixmap.save(path)
		if not saveSuccessful:
			raise IOError("Failed to save PNG: %s" % path)


class ThreadSignals(QtCore.QObject):
    """
    Signals must inherit from QObject, so this is a workaround to signal from a QRunnable object.
    We will use signals to communicate from the Worker class back to the ThreadPool.
    """
    finished = QtCore.Signal(int)
    stringSignal = QtCore.Signal(str)


"""Worker Template"""
class Worker(QtCore.QRunnable):
    """
    Executes code in a seperate thread.
    Communicates with the ThreadPool it spawned from via signals.
    """

    StatusOk = 0
    StatusError = 1

    def __init__(self):
        logging.info("Worker Class init")
        super(Worker, self).__init__()
        self.signals = ThreadSignals()

    def run(self):
        logging.info("worker run")
        status = Worker.StatusOk

        try:
            time.sleep(0.2)  # Process something big here.
        except Exception as e:
            logging.info (traceback.format_exc())
            status = Worker.StatusError
        self.signals.finished.emit(status)
        self.signals.stringSignal.emit("worker finished")


class ThreadPool(QtCore.QObject):
	"""
	Manages all Worker objects.
	This will receive signals from workers then communicate back to the main gui.
	"""
	poolStarted = QtCore.Signal(int)
	poolFinished = QtCore.Signal()
	workerFinished = QtCore.Signal(int)
	threadStringSignal = QtCore.Signal(str)

	def __init__(self, maxThreadCount=1, captureList=[]):
		QtCore.QObject.__init__(self)
		logging.info("ThreadPool Class Init")
		self._count = 0
		self._processed = 0
		self._has_errors = False

		self.pool = QtCore.QThreadPool()
		self.pool.setMaxThreadCount(maxThreadCount)
		self.captureList = captureList
		self.workspace = 'Compositing'

	def workerOnFinish(self, status):
		self._processed += 1

		# If a worker fails, indicate that an error happened.
		if status == Worker.StatusError:
			self._has_errors = True

		if self._processed == self._count:
			# Signal to gui that all workers are done.
			logging.info("ThreadPool has processed all workers")
			self.poolFinished.emit()

	def start(self):
		# Reset values.
		logging.info("ThreadPool Start")
		self._processed = 0
		self._has_errors = False
		self.workspace = hiero.ui.currentWorkspace()


		#Prepare the workers
		workers = []
		dagWrapper = DagWrapper()

		for captureTask in self.captureList:
			prepareDagWorker = PrepareDagWorker(dagWrapper)
			prepareDagWorker.workspace = captureTask.get('workspace', 'DagNabbit')
			prepareDagWorker.selectedNodes = captureTask.get('selectedNodes', nuke.allNodes())
			prepareDagWorker.fitDagToSelectedNodes = captureTask.get('fitDagToSelectedNodes', False)
			prepareDagWorker.margins = captureTask.get('margins', 100)
			prepareDagWorker.zoom = captureTask.get('zoom', 1.0)
			prepareDagWorker.highlightNodes = captureTask.get('highlightNodes', False)
			prepareDagWorker.delay = captureTask.get('windowDelay', 1.0)
			prepareDagWorker.signals.finished.connect(self.workerFinished)
			prepareDagWorker.signals.finished.connect(self.workerOnFinish)
			workers.append(prepareDagWorker)


			captureDagWorker = CaptureDagWorker(dagWrapper)
			captureDagWorker.imagePath = captureTask.get('imagePath', '/tmp/DagNabbit.png')
			captureDagWorker.nodeInfoPath = captureTask.get('nodeInfoPath', '/tmp/DagNabbit.info')
			captureDagWorker.delay = captureTask.get('captureDelay', 1.0)
			captureDagWorker.signals.finished.connect(self.workerFinished)
			captureDagWorker.signals.finished.connect(self.workerOnFinish)
			workers.append(captureDagWorker)

		# Reset workdspace when done
		resetWorkspaceWorker = ResetWorkspaceWorker(self.workspace)
		resetWorkspaceWorker.signals.finished.connect(self.workerFinished)
		resetWorkspaceWorker.signals.finished.connect(self.workerOnFinish)
		workers.append(resetWorkspaceWorker)


		# Signal to gui that workers are about to begin. You can prepare your gui at this point.
		self._count = len(workers)
		self.poolStarted.emit(self._count)

		# Create workers and connect signals to gui so we can update it as they finish.
		for worker in workers:
			self.pool.start(worker)


class Window(QtWidgets.QWidget):
	""" Progress Bar."""
	def __init__(self, captureList=[], parent=None):
		super(Window, self).__init__(parent)
		self.captureList = captureList

		# Create our main htread pool object that will handle all the workers and communication back to this gui.
		self.threadPool = ThreadPool(maxThreadCount=1, captureList=self.captureList)
		self.threadPool.poolStarted.connect(self.threadPoolOnStart)
		self.threadPool.poolFinished.connect(self.threadPoolOnFinish)
		self.threadPool.workerFinished.connect(self.workerOnFinish)

		self.progress_bar = QtWidgets.QProgressBar()

		self.main_layout = QtWidgets.QVBoxLayout()
		self.main_layout.addWidget(self.progress_bar)
		self.setLayout(self.main_layout)

		self.setWindowTitle("DagNabbit")
		self.resize(1024, 0)
		self.move(0,0)

		self.threadPool.start()

	def threadPoolOnStart(self, count):
		# Triggers right before workers are about to be created. Start preparing the gui to be in a "processing" state.
		self.progress_bar.setValue(0)
		self.progress_bar.setMaximum(count)

	def threadPoolOnFinish(self):
		# Triggers when all workers are done. At this point you can do a clean-up on your gui to restore it to it's normal idle state.
		if self.threadPool._has_errors:
			logging.info ("DagNabbit finished with errors!")
		else:
			logging.info ("DagNabbit finished successfully!")
		self.hide()

	def workerOnFinish(self, status):
		# Triggers when a worker is finished, where we can update the progress bar.
		logging.info(f"progress bar update, worker status: {status}")
		self.progress_bar.setValue(self.progress_bar.value() + 1)


def launch (captureList) -> None:
    logging.info("Running DagNabbit")
    global inst
    inst = Window(captureList)
    inst.show()
