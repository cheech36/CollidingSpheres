from __future__ import division
from visual import *
from visual.graph import *
import wx
import wx.lib.scrolledpanel
import numpy as np
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib.backends.backend_wxagg import Toolbar, FigureCanvasWxAgg
import matplotlib.pyplot as plt

import playerManager
from collision import CollisionMonitor


class SaveDialog(wx.Dialog):
    playerManager = None
    def __init__(self, *args, **kw):
        super(SaveDialog,self).__init__(*args, **kw)
        self.InitUI()
        self.SetSize((500, 150))
        self.SetTitle("Save Network")
        print("Saving ...")

    def InitUI(self):
        save_panel=wx.Panel(self)
        vbox_1 = wx.BoxSizer(wx.VERTICAL)
        hbox_1 = wx.BoxSizer(wx.HORIZONTAL)
        saveText = wx.StaticText(save_panel, label="Filename: ")
        self.filename = wx.TextCtrl(save_panel, size=(300, -1))
        self.submit = wx.Button(save_panel, size=(-1, 30), label="Save")
        self.submit.Bind(wx.EVT_BUTTON,self.OnSave)
        hbox_1.Add(saveText, flag=wx.LEFT, border=5)
        hbox_1.Add(self.filename, flag=wx.LEFT, border=5)
        hbox_1.Add(self.submit, flag=wx.LEFT, border=5)
        vbox_1.AddSpacer(50)
        vbox_1.Add(hbox_1, flag=wx.LEFT, border=15)
        save_panel.SetSizer(vbox_1)

    def OnSave(self,e):
        name = self.filename.GetValue()
        self.playerManager.save(name)
        self.Destroy()


class ControllPanel(wx.Frame):
    def __init__(self,title):
        ## Because MainWindow inherits wx.Frame, super is a call to the wx.Frame Constructor
        self.window1 = self.InitUI(title)



class DisplayPanel(wx.Frame):

    ENV = None
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

        SaveDialog.playerManager = self.playerManager
        save = SaveDialog(None,title='Save Neural Network')
        save.ShowModal()
        #print('Saving Disabled')
        save.Destroy()

    def OnPlayerChange(self,e):
        self.sc_player.SetRange(1,self.playerManager.playerCount)
        print(self.sc_player.GetValue() - 1, type(self.sc_player.GetValue()))
        self.playerManager.silent_Change( self.sc_player.GetValue() - 1)

    def OnBounceScroll(self,e):
        CollisionMonitor.restitution = self.bounce_slider.GetValue()/100

    def ToggleFriction(self,e):
        if(e == 'manager'):
            state = self.cb_friction.IsChecked()
            self.cb_friction.SetValue(not(state))
        else:
            self.playerManager.toggle_friction(True)



    def initControllPanel(self):
        self.controll_panel = wx.Panel(self.main_panel, -1, size=(250,450))
        vbox_cont = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        hbox6 = wx.BoxSizer(wx.HORIZONTAL)
        hbox7 = wx.BoxSizer(wx.HORIZONTAL)
        hbox8 = wx.BoxSizer(wx.HORIZONTAL)

        hbox1.Add(wx.StaticText(self.controll_panel,label='Active Player: '),flag=wx.LEFT, border = 20)
        self.sc_player = wx.SpinCtrl(self.controll_panel, value='1', size=(60,-1))

        self.sc_player.Bind(wx.EVT_SPINCTRL,self.OnPlayerChange)
        self.sc_player.SetRange(1,2)
        hbox1.Add(self.sc_player,flag=wx.LEFT, border=5)


        self.rb1 = wx.RadioButton(self.controll_panel, label='Normal', pos=(10, 10), style=wx.RB_GROUP)
        self.rb2 = wx.RadioButton(self.controll_panel, label='2x', pos=(10, 10))
        self.rb4 = wx.RadioButton(self.controll_panel, label='4x', pos=(10, 10))
        self.rb8 = wx.RadioButton(self.controll_panel, label='8x', pos=(10, 10))

        self.rb1.Bind(wx.EVT_RADIOBUTTON,self.SetSpeed)
        self.rb2.Bind(wx.EVT_RADIOBUTTON,self.SetSpeed)
        self.rb4.Bind(wx.EVT_RADIOBUTTON,self.SetSpeed)
        self.rb8.Bind(wx.EVT_RADIOBUTTON,self.SetSpeed)

        hbox5.Add(self.rb1,flag=wx.LEFT, border=5)
        hbox5.Add(self.rb2,flag=wx.LEFT, border=5)
        hbox5.Add(self.rb4,flag=wx.LEFT, border=5)
        hbox5.Add(self.rb8,flag=wx.LEFT, border=5)


        self.train_efficiency_msg = wx.TextCtrl(self.controll_panel, size=(50,-1))
        self.total_efficiency_msg = wx.TextCtrl(self.controll_panel, size=(50,-1))
        hbox6.Add(wx.StaticText(self.controll_panel, label='Efficiency: '), flag=wx.LEFT, border = 10)
        hbox7.Add(wx.StaticText(self.controll_panel, label='Training: '), flag = wx.LEFT, border = 10)
        hbox7.Add(self.train_efficiency_msg)
        hbox8.Add(wx.StaticText(self.controll_panel, label='Total: '), flag = wx.LEFT, border = 10)
        hbox8.Add(self.total_efficiency_msg)

        self.bounce_slider = wx.Slider(self.controll_panel, value=0, minValue=0, maxValue=100, size=(150,-1), style=wx.SL_HORIZONTAL)
        self.bounce_slider.Bind(wx.EVT_SCROLL,self.OnBounceScroll)

        hbox2.Add(wx.StaticText(self.controll_panel, label='Bounce: '), flag=wx.LEFT, border = 10)
        hbox2.Add(self.bounce_slider, flag=wx.ALIGN_CENTER)

        self.cb_friction = wx.CheckBox(self.controll_panel, label='Friction')
        self.cb_friction.Bind(wx.EVT_CHECKBOX, self.ToggleFriction)
        hbox3.Add(self.cb_friction, flag=wx.LEFT,border=10 )

        load_btn = wx.Button(self.controll_panel, label="Load Stats", size=(-1,30))
        load_btn.Bind(wx.EVT_BUTTON,self.load_player_stats)

        set_btn = wx.Button(self.controll_panel, label="Set Stats", size=(-1,30))
        set_btn.Bind(wx.EVT_BUTTON,self.set_player_stats)
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4.Add(load_btn)
        hbox4.Add(set_btn)


        vbox_cont.Add(hbox1, flag = wx.TOP, border=40)
        vbox_cont.Add(wx.StaticText(self.controll_panel, label='Training Speed: '), flag=wx.LEFT|wx.TOP, border = 10)
        vbox_cont.Add(hbox5, flag = wx.TOP, border = 0)
        vbox_cont.Add(hbox6, flag = wx.TOP, border = 10)
        vbox_cont.Add(hbox7, flag = wx.TOP, border = 10)
        vbox_cont.Add(hbox8, flag = wx.TOP, border = 10)
        vbox_cont.Add(hbox2, flag = wx.TOP, border = 10)
        vbox_cont.Add(hbox3, flag = wx.TOP, border = 10)
        vbox_cont.Add(hbox4, flag = wx.TOP|wx.ALIGN_CENTER, border = 10)
        self.playerPanel = wx.lib.scrolledpanel.ScrolledPanel(self.controll_panel,-1,size=(250,150))
        self.playerPanel.SetupScrolling()

        self.gridSizer_player = self.load_player_properties()

        self.playerPanel.SetSizer(self.gridSizer_player)
        self.playerPanel.SetBackgroundColour('#00ffff')
        self.controll_panel.SetSizer(vbox_cont)
        vbox_cont.Add(self.playerPanel, flag=wx.TOP, border=30)

        return self.controll_panel


    def load_player_stats(self,e):
        player = self.playerManager.getActivePlayer()
        for box in self.properties_txtCtrl:
            box.Clear()
        self.properties_txtCtrl[0].AppendText(str(player.getID()))
        self.properties_txtCtrl[1].AppendText(str(player.getType()))
        self.properties_txtCtrl[2].AppendText(str(player.mass))
        self.properties_txtCtrl[3].AppendText(str(player.position))
        self.properties_txtCtrl[4].AppendText(str(player.velocity))

        self.properties_txtCtrl[0].SetEditable(False)
        self.properties_txtCtrl[1].SetEditable(False)

        type = player.getType()
        if(type == "smartPlayer"):
            self.properties_txtCtrl[5].AppendText(str(player.sense.net_visible_f))

        #self.properties_txtCtrl[0]=str(player


    def load_player_properties(self):
        properties = ["ID:", "Type:", "Mass:","position","velocity", "net visible"]
        gs = wx.GridSizer(len(properties),2)
        self.properties_txtCtrl = []
        for property in properties:
            txt = wx.StaticText(self.playerPanel,label=property)
            gs.Add(txt)
            txt_ctrl = wx.TextCtrl(self.playerPanel,size=(100,-1))
            self.properties_txtCtrl.append(txt_ctrl)
            gs.Add(txt_ctrl)

        return gs


    def set_player_stats(self, e):
        player = self.playerManager.getActivePlayer()
        player.mass = int(self.properties_txtCtrl[2].GetValue())

        type = player.getType()
        if(type == "smartPlayer"):
            new_val = self.properties_txtCtrl[5].GetValue()
            if (new_val == "False"):
                player.sense.net_visible_f = False
                player.sense.remove_net_visual()
            elif (new_val == "True"):
                player.sense.net_visible_f = True
                player.sense.restore_net_visual()

    def SetSpeed(self, e):
        state1 = self.rb1.GetValue()
        state2 = self.rb2.GetValue()
        state3 = self.rb4.GetValue()
        state4 = self.rb8.GetValue()

        if state1:
            self.ENV.rate = 200
        elif state2:
            self.ENV.rate = 400
        elif state3:
            self.ENV.rate = 800
        elif state4:
            self.ENV.rate = 1600


class GraphPanel:
    def __init__(self, title):
        self.graph_window = window(menus=False, _make_panel=True, x=200, y=480, width=680, height=200, title=title)
        self.graph_display = gdisplay(window=self.graph_window, x=0, y=0, width=680, height=200)
        self.graph = gcurve(dot_color=color.cyan)



    def plot(self, point):
                x = point[0]
                y = point[1]
                self.graph.plot(pos=point)