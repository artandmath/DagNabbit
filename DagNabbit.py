import logging
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
    
def dagBBox() -> Tuple[int, int, int, int]:
	"""Calculate the bounding box for DAG"""
	nodes = nuke.allNodes()

	# Calculate the total size of the DAG
	min_x, min_y, max_x, max_y = [], [], [], []
	for node in nodes:
		min_x.append(node.xpos())
		min_y.append(node.ypos())
		max_x.append(node.xpos() + node.screenWidth())
		max_y.append(node.ypos() + node.screenHeight())    
	return (min(min_x), min(min_y), max(max_x), max(max_y))
	
class CaptureDag():
	"""for capturing screenshot of Nuke DAG"""
	def __init__(
			self,
			dag: QtOpenGL.QGLWidget,
			path: str = '',
			margins: int = 20,
			delay: float = 0.0,
			bbox: Tuple[int, int, int, int] = (-50, 50, -50, 50),
			zoom: float = 1.0
	) -> None:
		super(CaptureDag, self).__init__()
		self.dag = dag
		self.path = path
		self.margins = margins
		self.delay = delay
		self.bbox = bbox
		self.zoom = zoom
		self.successful = False
			
	def run(self) -> None:
		"""On thread start"""
		# Fetch DAG window size
		dagWindow = self.dag.window()
		dagWindowSize = dagWindow.size()

		# Calculate the total size of the DAG
		min_x, min_y, max_x, max_y = self.bbox
		zoom = self.zoom
		min_x -= int(self.margins / zoom)
		min_y -= int(self.margins / zoom)
		max_x += int(self.margins / zoom)
		max_y += int(self.margins / zoom)

		# Calculate the number of tiles required to cover all
		capture_width  = self.dag.width()
		capture_height = self.dag.height()

		image_width = int((max_x - min_x) * zoom)
		image_height = int((max_y - min_y) * zoom)
		
		center_x = max_x - image_width/2
		center_y = max_y - image_height/2

		self.dag.window().resize(image_width,image_height)			
		
		# Push window partially offscreen
		# A partially offscreen window will allowed to be bigger than the screen
		dagWindow = self.dag.window()
		if dagWindow.size().width() != image_width:
			#dagWindow.setWindowFlags(dagWindow.windowFlags() | QtCore.Qt.WA_X11NetWmWindowTypeDock)
			dagWindow.move(-50,0)
			dagWindow.resize(200,100)
			#dagWindow.setWindowFlags(dagWindow.windowFlags() & ~QtCore.Qt.WA_X11NetWmWindowTypeDock)
		else:
			# Resize the DAG to the full size beyond the window size
			dagWindow.resize(image_width,image_height)

						
		nuke.zoom (zoom, [center_x, center_y])
		time.sleep(2)
		
		# Create a pixmap to store the results
		pixmap = QtGui.QPixmap(image_width, image_height)
		painter = QtGui.QPainter(pixmap)
		painter.setCompositionMode(painter.CompositionMode_SourceOver)
		grabDagFramebuffer(self.dag, painter, 0, 0)
		painter.end()
		
		save_successful = pixmap.save(self.path)
		if not save_successful:
			raise IOError("Failed to save PNG: %s" % self.path)


def execute() -> None:
	logging.info("Running DagNabbit, Dag Nabbit")

	path = os.getenv("DagNabbitPath", default=os.path.expanduser("~")+"/Pictures/DagNabbit.png")
	margins = int(os.getenv("DagNabbitMargins", default="50"))
	zoom = float(os.getenv("DagNabbitZoom", default="1.0"))
	delay = float(os.getenv("DagNabbitDelay", default="0.0"))            

	# Get DAG or die trying
	dag = getDagWidget()
	if not dag:
		raise RuntimeError("Couldn't get DAG widget")
			
	# Capture Dag
	captureDag = CaptureDag(dag, bbox=dagBBox(), path=path, margins=margins,delay=delay)
	captureDag.run()
	


if __name__ == '__main__':
    execute()
