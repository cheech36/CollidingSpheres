from visual import *
from visual.graph import *
import wx
import numpy as np
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.backends.backend_wxagg import Toolbar, FigureCanvasWxAgg
import matplotlib.pyplot as plt

import playerManager




class ControllPanel(wx.Frame):
    def __init__(self,title):
        ## Because MainWindow inherits wx.Frame, super is a call to the wx.Frame Constructor
        self.window1 = self.InitUI(title)



class DisplayPanel(wx.Frame):
    def __init__(self, title, playerManager):
        super(DisplayPanel,self).__init__(None, title=title, size = (680,450))

        h = 450
        w = 500
        self.playerManager = playerManager
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        vbox_disp = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.main_panel = wx.Panel(self, -1)
        self.main_panel.SetBackgroundColour('#4f5049')

        self.dispPanel = wx.Panel(self.main_panel, -1,size=(380,450))
        """Begin Menu Bar"""
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        fitem1    = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        self.Bind(wx.EVT_MENU, self.OnQuit, fitem1)

        fitem2 = fileMenu.Append(wx.ID_SAVE, 'Save' ,'Save Network')
        self.Bind(wx.EVT_MENU, self.OnSave, fitem2)
        menubar.Append(fileMenu, '&File')

        self.SetMenuBar(menubar)
        """End Menu Bar"""



        self.msg = wx.TextCtrl(self.dispPanel,size=(w, h), style=wx.TE_MULTILINE)
        hbox1.Add(self.msg, proportion=0, flag=wx.EXPAND)

        self.nb = wx.Notebook(self.dispPanel)

        """Begin Tabs"""
        #Tab1
        self.tab1 = wx.Panel(self.nb)
        self.fig = Figure((5,4),75)
        self.axes = self.fig.add_subplot(111)
        self.canvas = FigureCanvasWxAgg(self.tab1, -1, self.fig)
        self.nb.AddPage(self.tab1,"Stream")

        #Tab2
        self.tab2 = wx.Panel(self.nb)
        t2 = wx.StaticText(self.tab2, label="Tensor Board Goes Here")
        self.nb.AddPage(self.tab2, "Network")
        """End Tabs"""

        hbox2.Add(self.nb, proportion=1, flag=wx.EXPAND| wx.BOTTOM)
        """
        self.ID_RANDOM = wx.NewId()
        b1 = wx.Button(self.main_panel, label='Random Plot', id=self.ID_RANDOM)
        hbox3.Add(b1, proportion = 0, flag = wx.EXPAND)
        self.Bind(wx.EVT_BUTTON, self.newPlot, id=self.ID_RANDOM)
        """
        vbox_disp.Add(hbox2, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=0)
        vbox_disp.Add(hbox3, flag=wx.CENTER)
        vbox_disp.Add(hbox1, proportion=0, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=0)

        self.dispPanel.SetSizer(vbox_disp)
        main_sizer.Add(self.dispPanel,1,wx.LEFT)
        self.contPanel = self.initControllPanel()
        main_sizer.Add(self.controll_panel,0,flag=wx.EXPAND|wx.RIGHT)

        self.main_panel.SetSizer(main_sizer)
        self.Move((200,0))
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

    def OnSave(self, e):
        self.msg.AppendText("Saving current state of Neural Network")

    def OnPlayerChange(self,e):
        self.sc_player.SetRange(1,self.playerManager.playerCount)
        print(self.sc_player.GetValue() - 1, type(self.sc_player.GetValue()))
        self.playerManager.silent_Change( self.sc_player.GetValue() - 1)





    def initControllPanel(self):
        self.controll_panel = wx.Panel(self.main_panel, -1, size=(300,450))
        vbox_cont = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(wx.StaticText(self.controll_panel,label='Active Player: '),flag=wx.LEFT, border = 20)
        self.sc_player = wx.SpinCtrl(self.controll_panel, value='1', size=(60,-1))

        self.sc_player.Bind(wx.EVT_SPINCTRL,self.OnPlayerChange)
        self.sc_player.SetRange(1,2)
        hbox1.Add(self.sc_player,flag=wx.LEFT, border=5)




        vbox_cont.Add(hbox1, flag = wx.TOP, border=40)
        self.controll_panel.SetSizer(vbox_cont)
        return self.controll_panel


class GraphPanel:
    def __init__(self, title):
        self.graph_window = window(menus=False, _make_panel=True, x=200, y=480, width=680, height=200, title=title)
        self.graph_display = gdisplay(window=self.graph_window, x=0, y=0, width=680, height=200)
        self.graph = gcurve(dot_color=color.cyan)



    def plot(self, point):
                x = point[0]
                y = point[1]
                self.graph.plot(pos=point)