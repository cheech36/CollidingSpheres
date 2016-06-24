from visual import *
from visual.graph import *
import wx
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import Toolbar, FigureCanvasWxAgg





class ControllPanel(wx.Frame):
    def __init__(self,title):
        ## Because MainWindow inherits wx.Frame, super is a call to the wx.Frame Constructor
        self.window1 = self.InitUI(title)



class DisplayPanel(wx.Frame):
    def __init__(self, title):
        super(DisplayPanel,self).__init__(None, title=title, size = (500,500))

        h = 500
        w = 500

        vbox1 = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.panel = wx.Panel(self, -1)
        self.panel.SetBackgroundColour('#4f5049')


        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        fitem    = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)
        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)

        self.msg = wx.TextCtrl(self.panel,size=(w, h), style=wx.TE_MULTILINE)
        hbox1.Add(self.msg, proportion=0, flag=wx.EXPAND)

        self.fig = Figure((5,4),75)
        self.axes = self.fig.add_subplot(111)

        self.canvas = FigureCanvasWxAgg(self.panel, -1, self.fig)
        hbox2.Add(self.canvas, proportion=1, flag=wx.EXPAND| wx.BOTTOM)

        self.ID_RANDOM = wx.NewId()
        b1 = wx.Button(self.panel, label='Random Plot', id=self.ID_RANDOM)
        hbox3.Add(b1, proportion = 0, flag = wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.newPlot, id=self.ID_RANDOM)

        vbox1.Add(hbox2, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=0)
        vbox1.Add(hbox3, flag=wx.CENTER)
        vbox1.Add(hbox1, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=0)


        self.panel.SetSizer(vbox1)
        self.Center()
        self.Show()

    def  newPlot(self, e):
        eid = e.GetId()

        if(eid == self.ID_RANDOM):
            self.msg.AppendText('Generating Random Plot\n')
            self.plot_Data = np.random.randint(8000, size=(14, 14))
            self.axes.imshow(self.plot_Data, interpolation='nearest')
            self.canvas._onSize(1)


    def OnQuit(self, e):
        self.Close()



class GraphPanel:
    def __init__(self, title):
        self.graph_window = window(menus=False, _make_panel=True, x=0, y=0, width=800, height=200, title=title)
        self.graph_display = gdisplay(window=self.graph_window, x=0, y=0, width=800, height=200)