import DagNabbit

captureList = [
    {
        "workspace": "DagNabbit",
        "selectedNodes": nuke.allNodes(),
        "margins": 100,
        "imagePath": "~/Pictures/DagNabbitAllNodes.png",
        "nodeInfoPath": "~/Pictures/DagNabbitAllNodes.info",
        "fitDagToSelectedNodes": False,
        "highlightNodes": False,
        "zoom": 1.0,
        "prepareWindowDelay": 1.0,
        "captureDelay": 1.0
    },
    {
        "workspace": "DagNabbit",
        "selectedNodes": nuke.allNodes(),
        "margins": 100,
        "imagePath": "~/Pictures/DagNabbitAllNodesHighlight.png",
        "nodeInfoPath": "~/Pictures/DagNabbitAllNodesHighlight.info",
        "fitDagToSelectedNodes": False,
        "highlightNodes": True,
        "zoom": 1.0,
        "windowDelay": 1.0,
        "captureDelay": 1.0
    },
    {
        "workspace": "DagNabbit",
        "selectedNodes": nuke.selectedNodes(),
        "margins": 100,
        "imagePath": "~/Pictures/DagNabbitSelectedNodesHighlight.png",
        "nodeInfoPath": "~/Pictures/DagNabbitSelectedNodesHighlight.info",
        "fitDagToSelectedNodes": False,
        "highlightNodes": True,
        "zoom": 1.0,
        "windowDelay": 1.0,
        "captureDelay": 1.0
    },
    {
        "workspace": "DagNabbit",
        "selectedNodes": nuke.selectedNodes(),
        "margins": 100,
        "imagePath": "~/Pictures/DagNabbitSelectedNodesFit.png",
        "nodeInfoPath": "~/Pictures/DagNabbitSelectedNodesFit.info",
        "fitDagToSelectedNodes": True,
        "highlightNodes": False,
        "zoom": 1.0,
        "windowDelay": 1.0,
        "captureDelay": 1.0
    },
    {
        "workspace": "DagNabbit",
        "selectedNodes": nuke.selectedNodes(),
        "margins": 100,
        "imagePath": "~/Pictures/DagNabbitSelectedNodesFitHighlight.png",
        "nodeInfoPath": "~/Pictures/DagNabbitSelectedNodesFitHighlight.info",
        "fitDagToSelectedNodes": True,
        "highlightNodes": True,
        "zoom": 1.0,
        "windowDelay": 1.0,
        "captureDelay": 1.0
    }
]

DagNabbit.launch(captureList)

