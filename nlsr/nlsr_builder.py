import os
from typing import List

from neighbor import Neighbor
from node import Node

logdir = "/var/logs/nlsr"

gamePrefix = "/com/stefanolupo/ndngame/0"
nameFormat = "node{nodeId}"

nlsrTemplateFile="./nlsr-template.conf"
topologyDirFormat="./topologies/{topologyName}"
nlsrOutputFormat="{name}-nlsr.conf"

neighborFormat = \
"neighbor  {{\n\
    name /com/stefanolupo/%C1.Router/router{nodeId}\n\
    face-uri  udp4://{nodeHostname}\n\
    link-cost {linkCost}\n\
}}\n\n"

pingFormat = "/{name}/ping"

advertisementsFormat = [
    "/discovery/broadcast",
    "/discovery/{name}",
    "/config/broadcast",
    "/config/{name}",

    "/{name}/blocks/sync",
    "/{name}/blocks/interact",
    "/{name}/status/sync",
    "/{name}/projectiles/sync",
    "/{name}/projectiles/interact",
]

def buildNeighbor(neighbor: Neighbor):
    node: Node = neighbor.node
    return neighborFormat.format(nodeId=node.nodeId, nodeHostname=node.hostname, linkCost=neighbor.linkCost)

def buildNeighbors(node: Node):
    return "\n".join([buildNeighbor(neighbor) for neighbor in node.neighborList])

def buildAdvertisement(lst, **kwargs):
    return ["\tprefix " + gamePrefix + item.format(**kwargs) for item in lst]

def buildAdvertisements(nodeName):
    advertisements = "\n".join(buildAdvertisement(advertisementsFormat, name=nodeName))
    return "\n\t{}\n".format(advertisements)

class NlsrBuilder:
    def __init__(self, topologyName="out", maxFacesPerPrefix=0):
        self.maxFacesPerPrefix = maxFacesPerPrefix
        self.topologyName = topologyName
    
    def buildNlsrFiles(self, nodes: List[Node]):
        for node in nodes:
            self.buildNlsrFile(node)

    def buildNlsrFile(self, node: Node):
        # Template needs:
        #   nodeId (for my router name)
        #   logdir
        #   neighbours
        #   maxFacesPerPrefix
        #   advertising

        neighbors = buildNeighbors(node)
        nodeName = nameFormat.format(nodeId=node.nodeId)

        advertisements = "prefix " + pingFormat.format(name=nodeName)
        if node.router is False:
            advertisements = advertisements + buildAdvertisements(nodeName)

        with open(nlsrTemplateFile) as templateFile:
            template = templateFile.read()
            template = template.replace("<nodeId>", node.nodeId)
            template = template.replace("<logdir>", logdir)
            template = template.replace("<neighbors>", neighbors)
            template = template.replace("<maxFacesPerPrefix>", str(self.maxFacesPerPrefix))
            template = template.replace("<advertising>", advertisements)
        
        topologyDirName = topologyDirFormat.format(topologyName=self.topologyName)
        if not os.path.exists(topologyDirName):
            os.mkdir(topologyDirName)
        
        nlsrConfFileName = nlsrOutputFormat.format(topologyName=self.topologyName, name=nodeName)
        fullFileName = os.path.join(topologyDirName, nlsrConfFileName)
        with open(fullFileName, 'w+') as outFile:
            outFile.write(template)

    def getNlsrFile(self):
        return nlsrOutputFormat.format()
