import itertools
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt2
import collections
import math
import pickle
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)


counter = 0
component = 0


class Point:
    def __init__(self, x, y, radius, id, state):
        self.x = x
        self.y = y
        self.radius = radius
        self.id = id
        self.state = state
        self.neighbour = 0


class MatplotlibWidget(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        loadUi("qt_designer.ui", self)

        self.point_dict = dict()
        self.i = 1
        self.radius = 0

        self.setWindowTitle("PyQt5 & Matplotlib Example GUI")

        self.next_bt.clicked.connect(self.update_graph)

        self.get_comp_bt.clicked.connect(self.get_points)

        self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))

        self.MplWidget.canvas.axes.grid()


    def get_points(self):
        global cid, fig, nr_comp

        nr_comp = int(self.nr_comp_le.text())

        fig = plt.figure(1)
        ax = fig.add_subplot(111)
        cid = self.MplWidget.canvas.mpl_connect('button_press_event', self.onclick)

    def onclick(self, event):
        global ix, iy

        global counter, component

        component += 1
        counter += 1
        point = Point(event.xdata*1000, event.ydata*1000, 0, counter, counter)

        global coords
        coords.append(point)

        if len(coords) == nr_comp:
            self.MplWidget.canvas.mpl_disconnect(cid)

        for element in coords:
            self.point_dict[element] = []

        return coords


    def update_graph(self):

        for point in coords:
            print(point.x, " ", point.y)
        with open('point_cloud.pkl', 'wb') as output:
            pickle.dump(coords, output, pickle.HIGHEST_PROTOCOL)
            output.close()

        infile = open('point_cloud.pkl', 'rb')
        new_dict = pickle.load(infile)
        infile.close()

        self.MplWidget.canvas.axes.clear()
        self.MplWidget.canvas.axes.grid()

        self.radius = 0.01 * self.i * 1000

        for point in coords:
            circle = plt2.Circle((point.x, point.y), self.radius, color='red', fill=False)
            point.radius = self.radius
            self.MplWidget.canvas.axes.add_artist(circle)
        self.connect_points(self.point_dict)
        self.travel_points(self.point_dict, coords[0])
        self.plot_state()

        self.i += 1

        self.radius_le.setText(str(self.radius))
        self.MplWidget.canvas.draw()

    def plot_state(self):
        for point in coords:
               self.MplWidget.canvas.axes.plot(point.x, point.y, 'o', color="black")
        self.current_nr_comp_le.setText(str(component))

    def circle_interference(self, x1, y1, x2, y2, r1, r2):
        distSq = (x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2)
        radSumSq = (r1 + r2) * (r1 + r2)
        # pont egymason
        if distSq == radSumSq:
            return 1
        # nem erintkeznek
        elif distSq > radSumSq:
            return -1
        # metszi egymast
        else:
            return 0

    def connect_points(self, point_dict):
        for element1, element2 in itertools.combinations(coords, 2):
            two_circle_interference = self.circle_interference(element1.x, element1.y, element2.x, element2.y,
                                                          element1.radius,
                                                          element2.radius)
            if two_circle_interference == 0 or two_circle_interference == 1:
                if element1 not in point_dict[element2] and element2 not in point_dict[element1]:
                    point_dict[element1].append(element2)
                    point_dict[element2].append(element1)
                    element1.neighbour += 1
                    element2.neighbour += 1
                    if element1.state != element2.state:
                        global component
                        component -= 1
                        self.current_nr_comp_le.setText(str(component))
                        if element1.state < element2.state:
                            self.bfs_state(point_dict, element1, element1.state)
                        else:
                            self.bfs_state(point_dict, element1, element2.state)
                self.MplWidget.canvas.axes.plot([element1.x, element2.x], [element1.y, element2.y])
        current_state = coords[0].state
        for point in coords:
            if current_state != point.state:
                self.travel_points(point_dict, point)
                current_state = point.state
        self.bfs(point_dict, element1)

    def color_triangle(self, xcoord, ycoords):
        self.MplWidget.canvas.axes.fill(xcoord, ycoords)

    def bfs_state(self, graph, root, state):
        visited, queue = set(), collections.deque([root])
        visited.add(root)
        while queue:
            vertex = queue.popleft()
            for neighbour in graph[vertex]:
                neighbour.state = state
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(neighbour)

    def bfs(self, graph, root):
        visited, queue = set(), collections.deque([root])
        visited.add(root)
        while queue:
            vertex = queue.popleft()
            for neighbour in graph[vertex]:
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(neighbour)

        circle = True
        for element in graph:
            if element.neighbour < 2:
                circle = False

        if len(visited) == len(graph) and circle:
            self.nr_hole_le.setText("1")

            pointTopointDict = dict()

            for element in graph:
                pointTopointDict[element] = []

            for element1, element2 in itertools.combinations(coords, 2):
                pointTopointDict[element1].append(math.sqrt(((element1.x - element2.x) ** 2) +
                                                            ((element1.y - element2.y) ** 2)))
                pointTopointDict[element2].append(math.sqrt(((element1.x - element2.x) ** 2) +
                                                            ((element1.y - element2.y) ** 2)))

            minValueFromAllPointToPoint = []

            for element in graph:
                minValueFromAllPointToPoint.append(max(pointTopointDict[element]))

            print(min(minValueFromAllPointToPoint))

            if min(minValueFromAllPointToPoint) <= 2 * self.radius:
                self.nr_hole_le.setText("0")

    def travel_points(self, pointDict, root):
        coordx = []
        coordy = []
        visited, queue = set(), collections.deque([root])
        visited.add(root)
        while queue:
            vertex = queue.popleft()
            for neighbour in pointDict[vertex]:
                for neighbour2 in pointDict[neighbour]:
                    for neighbour3 in pointDict[neighbour2]:
                        if neighbour3 == vertex:
                            coordx.append(neighbour.x)
                            coordx.append(neighbour2.x)
                            coordx.append(neighbour3.x)
                            coordy.append(neighbour.y)
                            coordy.append(neighbour2.y)
                            coordy.append(neighbour3.y)
                            self.color_triangle(coordx, coordy)
                            coordy.clear()
                            coordx.clear()
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(neighbour)

global radius


coords = []

def main():

    app = QApplication([])
    window = MatplotlibWidget()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()