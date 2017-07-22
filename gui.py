import sys

import wx
import wx.lib.mixins.listctrl as listmix
from wx.lib.splitter import MultiSplitterWindow

from visual_report import VisualReport
from todotool import TaskList

# Model:
# ======
# - `data` contains the complete extension of tuples.
# - `temp_data` only contains the currently matching tuples from `data`.
# - The ListCtrl only displays the content of `temp_data`.


# TODO:
# =====
# - Manage colors centrally
# - Make everything more dynamic
# - Color coding
# - Icons
# - Warning message for duplicate tasks
# - Fix np/jk item selection in ListCtrl for first and las item
# - Change selection background color to black or white in the list ctrl
# - Have a look at the following wxPyton demos:
#       + "Miscellaneous -> OGL"
#       + "Miscellaneous -> DragScroller"
#       + "Miscellaneous -> FileHistory"
#       + "Using Images -> ArtProvider"
#       + "Process and Events"
#       + "More Windows/Controls -> MVCTree"
#       + "More Windows/Controls -> MaskedEditControls"
#       + "More Windows/Controls -> PyPlot"
#       + "More Windows/Controls -> SplitTree"
#       + "More Windows/Controls -> TreeMixin"
#       + "Advanced Generic Widgets -> AquaButton"
#       + "Advanced Generic Widgets -> CustonTreeCtrl"
#       + "Advanced Generic Widgets -> GradientButton"
#       + "Advanced Generic Widgets -> HyperTreeList"
#       + "Advanced Generic Widgets -> LabelBook"
#       + "Advanced Generic Widgets -> UltimateListCtrl"
#       + "Custom Controls -> ComboTreeBox"
#       + "Custom Controls -> GenericButtons"
#       + "Custom Controls -> GenericDirCtrl"
#       + "Custom Controls -> ItemsPicker"
#       + "Custom Controls -> MultiSash"
#       + "Custom Controls -> PlateButton"
#       + "Custom Controls -> TreeListCtrl"
#       + "Window Layout"


data = TaskList()

temp_data = TaskList()

# Structure of a key-value pair:
#
# priority: [(evenBgColour, oddBgColour), FgColourBit]
#
# FgColourBit:
# - 1: black
# - 0: white
#
# oddBgColours are darker than evenBgColours
priority_colors_even_odd = {
    1: [(wx.Colour(210, 0, 0), wx.Colour(255, 40, 40)), 0],       # red
    2: [(wx.Colour(215, 125, 0), wx.Colour(255, 165, 40)), 1],    # orange
    3: [(wx.Colour(215, 215, 0), wx.Colour(255, 255, 40)), 1],    # yellow
    4: [(wx.Colour(84, 212, 0), wx.Colour(124, 252, 40)), 1],     # green
    5: [(wx.Colour(95, 166, 210), wx.Colour(135, 206, 250)), 1],  # light blue
    6: [(wx.Colour(25, 65, 185), wx.Colour(65, 105, 225)), 0],    # dark blue
    7: [(wx.Colour(107, 72, 179), wx.Colour(147, 112, 219)), 1],  # purple
    }
priority_colors = {
    1: [(wx.Colour(255, 40, 40), wx.Colour(255, 40, 40)), 0],      # red
    2: [(wx.Colour(255, 165, 40), wx.Colour(255, 165, 40)), 1],    # orange
    3: [(wx.Colour(255, 255, 40), wx.Colour(255, 255, 40)), 1],    # yellow
    4: [(wx.Colour(124, 252, 40), wx.Colour(124, 252, 40)), 1],    # green
    5: [(wx.Colour(135, 206, 250), wx.Colour(135, 206, 250)), 1],  # light blue
    6: [(wx.Colour(65, 105, 225), wx.Colour(65, 105, 225)), 0],    # dark blue
    7: [(wx.Colour(147, 112, 219), wx.Colour(147, 112, 219)), 1],  # purple
    }

class GUI(object):
    def __init__(self, model):
        self.model = model
        self.app = wx.App(False)
        self.frame = TodoFrame(None, 'GUI test')
        self.frame.register(model)
        self.app.MainLoop()


class TodoFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent=parent, title=title, size=(400, 400))

        self.model = None
        self.parent = parent

        self.edit_window_visible = False

        self.k1 = ''
        self.k2 = ''
        self.k3 = ''
        self.listen()

        self.status_bar = TodoStatusBar(self)
        self.SetStatusBar(self.status_bar)

        self.switch = False

        # Menu entries
        self.button_menu_ID1 = wx.NewId()
        self.button_menu_ID2 = wx.NewId()
        self.button_menu_ID3 = wx.NewId()
        self.button_menu_ID4 = wx.NewId()
        self.Bind(wx.EVT_MENU, self.OnMenuEntrySort,
                  id=self.button_menu_ID1)
        self.Bind(wx.EVT_MENU, self.OnMenuEntryInfo,
                  id=self.button_menu_ID2)
        self.Bind(wx.EVT_MENU, self.OnMenuEntryVisualReport,
                  id=self.button_menu_ID3)
        self.Bind(wx.EVT_MENU, self.OnMenuEntryToggleEditWindow,
                  id=self.button_menu_ID4)

        # Multiple keybindings states
        self.state_C_x_ID = wx.NewId()
        self.state_ID2 = wx.NewId()
        self.state_undo_ID = wx.NewId()
        self.Bind(wx.EVT_MENU, self.OnState_C_x,
                  id=self.state_C_x_ID)
        self.Bind(wx.EVT_MENU, self.OnState2,
                  id=self.state_ID2)
        self.Bind(wx.EVT_MENU, self.OnStateUndo,
                  id=self.state_undo_ID)

        self.accelerator_entries = [
            # Single keybindings
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('S'), self.button_menu_ID1),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('I'), self.button_menu_ID2),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('R'), self.button_menu_ID3),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('E'), self.button_menu_ID4),
            # Multiple keybindings
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('x'), self.state_C_x_ID),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('f'), self.state_ID2),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('g'), self.state_undo_ID)
            ]
        self.accelerator_table = wx.AcceleratorTable(self.accelerator_entries)
        self.SetAcceleratorTable(self.accelerator_table)

        # temp_data must not be empty for selection to work correctly
        self.update_temp_data()

        self.main_panel = wx.Panel(self)
        self.main_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        self.main_splitter = MultiSplitterWindow(
            self.main_panel, style=wx.SP_LIVE_UPDATE|wx.SP_BORDER)
        self.main_splitter.SetOrientation(wx.HORIZONTAL)

        # self.main_splitter.SetMinimumPaneSize(0)

        self.panel = TodoListCtrlPanel(self.main_splitter)
        self.panel.get_listctr().colorize()
        self.SetBackgroundColour(wx.Colour(255, 119, 0))

        self.edit_window = TodoEditWindow(self.main_splitter)
        self.edit_window.Hide()

        self.main_splitter.AppendWindow(self.panel, self.GetSize()[1] / 3 * 2)

        self.search_box = SearchBox(self)

        self.panel.get_listctr().brother_widget = self.search_box
        # self.Bind(wx.EVT_CHAR_HOOK, self.OnSearch, self.search_box)
        self.search_box.Bind(wx.EVT_TEXT, self.OnSearch, self.search_box)
        # self.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)  #, self.search_box)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch)  #, self.search_box)
        # self.Bind(wx.EVT_CHAR, self.OnBackspace, self.search_box)
        # self.Bind(wx.EVT_CHAR_HOOK, self.OnEnter)  # , self.search_box)
        self.Bind(wx.EVT_SET_FOCUS, self.OnBackspace, self.search_box)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnBackspace, self.search_box)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnBackspace, self.search_box)
        self.Bind(wx.EVT_SIZE, self.OnSize, self)
        self.search_box.Bind(wx.EVT_CHAR, self.OnChar, self.search_box)

        self.search_box.SetFocus()

        self.main_slider = wx.Slider(
            # self, 100, 25, 1, 100, (30, 60), (250, -1),
            self.status_bar, 100, 25, 1, len(temp_data), (30, 60), (250, -1),
            wx.SL_HORIZONTAL|wx.SL_AUTOTICKS)  # |wx.SL_LABELS)
        self.main_slider.SetTickFreq(5, 1)
        self.main_slider.SetLineSize(5)
        self.main_slider.SetPageSize(5)
        self.main_slider.SetBackgroundColour(wx.Colour(80, 80, 80))
        self.main_slider.Bind(wx.EVT_SLIDER,
                                self.OnSlider,
                                self.main_slider)
        # TODO: Add text for current value or move it somewhere else
        # self.main_slider.SetPosition((self.status_bar.GetFieldRect(1).x+200, 0))

        self.addTaskButton = wx.Button(self, 0, 'Add &task')  # , size=(125, -1))
        self.addTaskButton.SetBackgroundColour(wx.Colour(255, 77, 0))
        self.addTaskButton.Bind(wx.EVT_BUTTON,
                                self.OnClickAddTaskButton,
                                self.addTaskButton)

        self.setPriorityButton = wx.Button(self, 0, 'Set &priority')
        self.setPriorityButton.SetBackgroundColour(wx.Colour(255, 77, 0))
        self.setPriorityButton.Bind(wx.EVT_BUTTON,
                                    self.OnClickSetPriorityButton,
                                    self.setPriorityButton)

        self.deleteTaskButton = wx.Button(self, 0, '&Delete task')
        self.deleteTaskButton.SetBackgroundColour(wx.Colour(255, 77, 0))
        self.deleteTaskButton.Bind(wx.EVT_BUTTON,
                                    self.OnClickDeleteTaskButton,
                                    self.deleteTaskButton)

        self.moreButton = wx.Button(self, 0, '&More')
        self.moreButton.SetBackgroundColour(wx.Colour(255, 77, 0))
        self.moreButton.Bind(wx.EVT_BUTTON,
                                    self.OnClickMoreButton,
                                    self.moreButton)

        self.main_panel_sizer.Add(self.main_splitter, 1, wx.EXPAND|wx.ALL)
        self.main_panel.SetSizer(self.main_panel_sizer)
        self.main_splitter.Layout()
        self.main_panel.Layout()

        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.panel.sizer.Layout()
        # self.buttonSizer.Add(self.main_slider, 0, wx.ALIGN_LEFT|wx.ALL)
        self.buttonSizer.Add(self.addTaskButton, 0, wx.ALIGN_LEFT|wx.ALL)
        self.buttonSizer.Add(self.setPriorityButton, 0, wx.ALIGN_RIGHT|wx.ALL)
        self.buttonSizer.Add(self.deleteTaskButton, 0, wx.ALIGN_RIGHT|wx.ALL)
        self.buttonSizer.Add(self.moreButton, 0, wx.ALIGN_RIGHT|wx.ALL)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.search_box, 0, wx.GROW|wx.ALL, 6)
        # self.sizer.Add(self.addTaskButton, 0, wx.ALIGN_RIGHT|wx.ALL)
        # self.sizer.Add(self.setPriorityButton, 0, wx.ALIGN_RIGHT|wx.ALL)
        self.sizer.Add(self.buttonSizer, 0, wx.ALIGN_RIGHT|wx.ALL)
        self.sizer.Add(self.main_panel, 1, wx.EXPAND|wx.ALL)
        # self.sizer.Add(self.panel, 1, wx.EXPAND|wx.ALL)
        # self.sizer.Add(self.edit_window, 1, wx.EXPAND|wx.ALL)
        # self.sizer.Add(self.main_splitter, 1, wx.EXPAND|wx.ALL)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.Show(True)

    def register(self, model):
        self.model = model

    def OnSlider(self, event):
        print self.main_slider.GetValue()
        self.main_slider.SetRange(1, len(temp_data))

        # previous = 0
        # next = 0
        current  = self.main_slider.GetValue()

        # # XXX
        # # This would be more efficient, but it does not check
        # # milliseconds/nanoseconds yet.
        # if current > 0:
        #     previous = self.main_slider.GetValue() - 1
        # else:
        #     previous = self.main_slider.GetMax() - 1
        # if current < self.main_slider.GetMax():
        #     next = self.main_slider.GetValue() + 1
        # else:
        #     next = 0

        # self.panel.get_listctr().SetItemState(previous, 0, -1)
        # self.panel.get_listctr().SetItemState(next, 0, -1)

        # This can become inefficient for large lists.
        item = 0
        while True:
            item = self.panel.get_listctr().GetNextItem(item, wx.LIST_NEXT_ALL,
                                                        wx.LIST_STATE_SELECTED)
            if item == -1:
                break

            self.panel.get_listctr().SetItemState(
                item, 0, wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)

        self.panel.get_listctr().SetItemState(
            current-1, wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED,
            wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)

        self.panel.get_listctr().EnsureVisible(current)
        self.panel.get_listctr().SetFocus()

        event.Skip()

    def OnSize(self, event):
        # TODO: Make param of SetSashPosition dynamic
        self.main_splitter.SetSashPosition(0, self.GetSize()[0] / 3 * 2)
        event.Skip()

    def OnState_C_x(self, event):
        print 'C-x  -  SWITCH: ', self.switch
        self.switch = True
        event.Skip()

    def OnState2(self, event):
        print 'C-x  -  SWITCH: ', self.switch
        if self.switch:
            self.OnMenuEntrySort(event)
        event.Skip()

    def OnStateUndo(self, event):
        print 'C-x  -  SWITCH: ', self.switch
        self.switch = False
        event.Skip()

    def listen(self):
        # keycode =  event.GetKeyCode()
        self.Bind(wx.EVT_KEY_DOWN, self._OnFirstChar)
        self.Bind(wx.EVT_KEY_DOWN, self._OnSecondChar)
        self.Bind(wx.EVT_KEY_DOWN, self._OnThirdChar)

        # if keycode == wx.WXK_TAB:
        if self.k1 == wx.WXK_TAB:
            if self.k2 == 'x':
                if self.k3 == 'j':
                    self.OnMenuEntrySort()

    def _OnFirstChar(self, event):
        print "foo"*80
        self.k1 = event.GetKeyCode()

    def _OnSecondChar(self, event):
        self.k2 = chr(event.GetKeyCode())

    def _OnThirdChar(self, event):
        self.k3 = chr(event.GetKeyCode())

    def OnMenuEntrySort(self, event):
        self._sort_temp_data()
        self._reload_view(do_reload_temp_data=False)

    def OnMenuEntryInfo(self, event):
        dialog = wx.MessageDialog(self,
                                  'This is some information. ',
                                  'Info', wx.OK|wx.ICON_INFORMATION)
        dialog.ShowModal()
        dialog.Destroy()

    def OnMenuEntryVisualReport(self, event):
        VisualReport(title='Report', data=data)
        event.Skip()

    def OnMenuEntryToggleEditWindow(self, event):
        if not self.edit_window_visible:
            self.main_splitter.AppendWindow(self.edit_window)
            self.edit_window.Show()
            self.edit_window_visible = True
        else:
            self.main_splitter.DetachWindow(self.edit_window)
            self.edit_window.Hide()
            self.edit_window_visible = False

    def OnChar(self, event):
        if event.GetKeyCode() == 9:  # TAB
            self.panel.get_listctr().SetFocus()
        elif event.GetKeyCode() == 13:  # ENTER
            print 'ENTER'
        else:
            event.Skip()

    def OnClickAddTaskButton(self, event):
        dialog = wx.TextEntryDialog(self, 'New task:', 'TASK', 'TODO')
        dialog.SetValue('TASK')
        new_task = ''
        if dialog.ShowModal() == wx.ID_OK:
            new_task = dialog.GetValue()

            choice_dialog = wx.SingleChoiceDialog(self,
                                                  'Select priority', 'Priority',
                                                  [str(i) for i in xrange(1, 8)],  # TODO: Make dynamic
                                                  wx.CHOICEDLG_STYLE)
            if choice_dialog.ShowModal() == wx.ID_OK:
                new_priority = int(choice_dialog.GetStringSelection())

                self.model.add_task(new_task, new_priority)  # Append to the model
                # data.append([new_task, new_priority])  # Append to the views data list

                # Redisplay the list
                self._reload_view()
            choice_dialog.Destroy()

        dialog.Destroy()

    def OnClickSetPriorityButton(self, event):
        # FIXME: Does not set the priority for the right items yet
        # for idx in self.panel.get_listctr().GetSelectedItems():
        # while self.panel.get_listctr().GetNextSelected(0):
            # print "%10s %s" % (idx, self.temp[idx])

        # for idx, item in enumerate(self.panel.get_listctr().temp):
        #     if item.IsSelected:
        #         print item

        print "``````````", self.panel.get_listctr().selected_items

        for sel_item in self.panel.get_listctr().selected_items:
            dialog = wx.SingleChoiceDialog(self,
                                           'Select priority', 'Priority',
                                           [str(i) for i in xrange(1, 8)],
                                           wx.CHOICEDLG_STYLE)
            if dialog.ShowModal() == wx.ID_OK:
                print 'Item: %s; Selection %s' % (sel_item, dialog.GetStringSelection())
                for idx, item in enumerate(data.get_as_list()):
                    if sel_item.label == item.label:
                        new_priority = int(dialog.GetStringSelection())
                        print 'INDEX: ', self.model.task_list.get_task_at(idx)
                        self.model.set_priority(idx, new_priority)  # Set for the model
                        data.get_task_at(idx).priority = new_priority  # Set for the views data list
                        print "NEW: ", item.label, ' - ', new_priority

                        # Redisplay the list
                        self._reload_view()

            dialog.Destroy()

    def OnClickDeleteTaskButton(self, event):
        choice_dlg = wx.SingleChoiceDialog(self,
                                           'Really delte the following task(s)?',
                                           'Delete',
                                           [i[0] + ' (priority: ' + str(i[1]) + ')' for i in self.panel.get_listctr().selected_items],
                                           wx.CHOICEDLG_STYLE)
        if choice_dlg.ShowModal() == wx.ID_OK:
            # new_priority = int(choice_dlg.GetStringSelection())

            for item in self.panel.get_listctr().selected_items:
                for idx, task in enumerate(data):
                    if item == task:
                        self.model.remove_task((idx + 1))  # Remove from the model
                        data.pop(idx - 1)  # Remove from the views data list

                        # Redisplay the list
                        self._reload_view()
                        break
        choice_dlg.Destroy()

    def OnClickMoreButton(self, event):
        # self._sort_temp_data()
        # self._reload_view(do_reload_temp_data=False)

        button_menu = wx.Menu()
        button_menu.Append(self.button_menu_ID1, '&Sort\tCtrl+S/C-x C-f')
        button_menu.Append(self.button_menu_ID2, '&Info\tCtrl+I')
        button_menu.Append(self.button_menu_ID3, 'Visual &Report\tCtrl+R')
        button_menu.Append(self.button_menu_ID4, 'Toggle &Edit window\tCtrl+E')
        self.PopupMenu(button_menu, self.moreButton.GetPosition())
        button_menu.Destroy()

    def OnSearch(self, event):
        # value = self.search_box.GetValue()
        # if not value:
        #     print 'Nothing entered'
        #     return
        # keycode = event.GetKeyCode()

        current = str(self.search_box.GetValue())
        # current = str(self.search_box.GetLineText(0))

        # wx.KeyEvent(wx.WXK_RETURN)

        # current = str(self.search_box.GetRange(0, self.search_box.GetInsertionPoint()))
        # current = str(self.search_box.GetValue())

        # self.update_temp_data(current)

        # print 'KEYCODE: ', keycode
        # if keycode == 8:  # Backspace key
        if False: # TODO: Improve or remove
            self.panel.get_listctr().ClearAll()
            self._clear_temp_data()
        else:
            print 'CURRENT: ', current
            # self.panel.get_listctr().update(current)
            self.panel.get_listctr().ClearAll()
            # self._clear_temp_data()
            self.update_temp_data(current)
            self.panel.get_listctr().Populate(temp_data)
            self.Layout()
        event.Skip()

    def _reload_view(self, do_reload_temp_data=True):
        self.panel.get_listctr().ClearAll()
        if do_reload_temp_data:
            self.update_temp_data()
        self.panel.get_listctr().Populate(temp_data)
        self.Layout()

    def _clear_temp_data(self):
        temp_data.clear()

    def OnBackspace(self, event):
        keycode = event.GetKeyCode()
        print 'KEYCODE: ', keycode
        if keycode == 8:  # Backspace key
            self.panel.get_listctr().ClearAll()
        else:
            self.OnSearch(event)

    def OnEnter(self, event):
        keycode = event.GetKeyCode()
        print 'KEYCODE: ', keycode

    def update_temp_data(self, string=''):
        self._clear_temp_data()
        for item in data.get_as_list():
            if string in item.label or string in str(item.priority):
                # print 'MATCH: ', item
                temp_data.add(item)
        self.status_bar.set_tasks(len(temp_data))

    def _sort_temp_data(self):
        temp_data.sort_alphabetically()
        temp_data.sort_numerically()


class SearchBox(wx.TextCtrl):
    def __init__(self, parent, value=-1, text='',
                 size=(125, -1), style=wx.TE_PROCESS_ENTER):
        wx.TextCtrl.__init__(self, parent, value, text, size)
        self.SetBackgroundColour(wx.Colour(255, 77, 0))     # sort alphabethically
        self.SetForegroundColour(wx.Colour(255, 255, 255))  # sort numerically

    # def OnKeyDown(self):
    #     self.OnSearch()

    # def OnSearch(self):
    #     print 'Key down'


class TodoListCtrl(wx.ListCtrl,
                   listmix.ListCtrlAutoWidthMixin):
                   # , listmix.TextEditMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        self.items = data
        self.temp = self.items
        self.selected_items = []
        self.current_item_idx = 0
        # Widget that is associated with this ListCtrl for easy TAB switching
        self.brother_widget = None

        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        self.image_list = wx.ImageList(16, 16)
        self.p0_img = self.image_list.Add(wx.Bitmap('res/images/contact-new.png'))
        self.p1_img = self.image_list.Add(wx.Bitmap('res/images/go-next.png'))
        self.p2_img = self.image_list.Add(wx.Bitmap('res/images/media-record.png'))
        self.p3_img = self.image_list.Add(wx.Bitmap('res/images/process-stop.png'))
        # self.testImage = self.image_list.Add(
        #     wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE,
        #                              wx.ART_OTHER, (16, 16)))
        self.SetImageList(self.image_list, wx.IMAGE_LIST_SMALL)

        self.Bind(wx.EVT_CHAR, self.OnCharListCtrl)
        # self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list)
        # self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected, self.list)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)

        # self.SetBackgroundColour(wx.Colour(255, 156, 69))
        self.SetBackgroundColour(wx.Colour(50, 50, 50))
        self.Populate(self.items)

        listmix.ListCtrlAutoWidthMixin.__init__(self)
        # listmix.TextEditMixin.__init__(self)

    def OnItemSelected(self, event):
        # current = event.m_itemIndex
        item_idx = event.GetIndex()
        self.current_item_idx = item_idx
        print '++++++++++++ ', item_idx
        self.selected_items.append(temp_data.get_task_at(item_idx))
        print 'SELECTED_ITEMS: ', self.selected_items
        event.Skip()

    def OnItemDeselected(self, event):
        item_idx = event.GetIndex()
        print '------------ ', item_idx
        del self.selected_items[:]

    def OnCharListCtrl(self, event):
        steps = 5;
        if event.GetKeyCode() == 9:  # TAB
            # self.panel.get_listctr().SetFocus()
            # print 'TAB'
            self.brother_widget.SetFocus()
        elif event.GetKeyCode() == 13:  # ENTER
            # print 'ENTER'
            info = '%-15s %s\n%s\n%-15s %s' % ('TASK:',
                                               temp_data.get_task_at(self.current_item_idx).label,
                                               '-' * (len(temp_data.get_task_at(self.current_item_idx).label) + 30),
                                               'PRIORITY:',
                                               str(temp_data.get_task_at(self.current_item_idx).priority))
            dialog = wx.MessageDialog(self, str(info), 'Info', wx.OK|wx.ICON_INFORMATION)
            dialog.ShowModal()
            dialog.Destroy()
        elif event.GetKeyCode() == 110:  # 'n' keys
            # self._deselect_all_items()
            self.SetItemState(self.current_item_idx, 0, -1)
            self.EnsureVisible(self.current_item_idx)
            if self.current_item_idx < self.GetItemCount() - 1:
                self.SetItemState(self.current_item_idx+1,
                                  wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED,
                                  wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)
                self.EnsureVisible(self.current_item_idx)
            else:
                # Jumps to the first item if the last list item + 1 is reached
                self.SetItemState(0,
                                  wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED,
                                  wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)
                self.EnsureVisible(self.current_task_idx)
        elif event.GetKeyCode() == 106:  # 'j' key
            # Larger steps for faster forward navigation
            # self._deselect_all_items()
            self.SetItemState(self.current_item_idx, 0, -1)
            self.EnsureVisible(self.current_item_idx)
            diff = self.GetItemCount() - self.current_item_idx
            if diff > steps:  # self.current_item_idx < self.GetItemCount() - steps:
                self.SetItemState(self.current_item_idx+steps,
                                  wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED,
                                  wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)
                self.EnsureVisible(self.current_item_idx)
            else:
                # Jumps to the first item if the last list item + 1 is reached
                self.SetItemState(0,
                                  wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED,
                                  wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)
                self.EnsureVisible(self.current_task_idx)
        elif event.GetKeyCode() == 112:  # 'p' key
            # self._deselect_all_items()
            self.SetItemState(self.current_item_idx, 0, -1)
            self.EnsureVisible(self.current_item_idx)
            if self.current_item_idx > 0:
                self.SetItemState(self.current_item_idx-1,
                                  wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED,
                                  wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)
                self.EnsureVisible(self.current_item_idx)
            else:
                # Jumps to the last item if the first list item - 1 is reached
                self.SetItemState(self.GetItemCount()-1,
                                  wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED,
                                  wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)
                self.EnsureVisible(self.GetItemCount())
        elif event.GetKeyCode() == 107:  # k' key
            # Larger steps for faster backward navigation
            # self._deselect_all_items()
            self.SetItemState(self.current_item_idx, 0, -1)
            self.EnsureVisible(self.current_item_idx)
            diff = self.GetItemCount() - self.current_item_idx
            if self.current_item_idx > steps:
                self.SetItemState(self.current_item_idx-5,
                                  wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED,
                                  wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)
                self.EnsureVisible(self.current_item_idx)
            else:
                # Jumps to the last item if the first list item - 1 is reached
                self.SetItemState(self.GetItemCount()-1,
                                  wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED,
                                  wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)
                self.EnsureVisible(self.GetItemCount())
        else:
            event.Skip()
        # print event.GetKeyCode()

    def _deselect_all_items(self):
        item = -1
        while True:
            item = self.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)

            if item == -1:
                break

            if item != wx.LIST_STATE_SELECTED:
                self.SetItemState(item, 0, -1)

    def Populate(self, content):
        for idx, fieldname in enumerate(content.get_task_at(0).fields.keys()):
            self.InsertColumn(idx, fieldname)

        # for idx, data in enumerate(self.items):
        index = 0
        # for idx, data in enumerate(content):
        for idx, data in enumerate(content.get_as_list()):
            # self.SetStringItem(idx, 1, str(data))

            # index = self.InsertStringItem(sys.maxint, str(data))
            # self.SetStringItem(idx, 0, str(data[0]))
            # self.SetStringItem(idx, 1, str(data[1]))

            if data.priority == 1:
                index = self.InsertImageStringItem(sys.maxint, str(data.label), self.p1_img)
            else:
                index = self.InsertImageStringItem(sys.maxint, str(data.label), self.p2_img)
            self.SetStringItem(index, 1, str(data.priority))
            self.SetStringItem(index, 0, str(data.label))
            self.SetItemData(index, idx)

        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)

        self.colorize()

        self.currentItem = 0

    def update(self, string):
        for item in self.items:
            if string in item[0]:
                self.temp.append(item)

        self.Populate(self.temp)

    def SetStringItem(self, index, col, data):
        if col in range(3):
            wx.ListCtrl.SetStringItem(self, index, col, data)
            # wx.ListCtrl.SetStringItem(self, index, col+3, str(len(data)))
        else:
            try:
                datalen = int(data)
            except:
                return

            wx.ListCtrl.SetStringItem(self, index, col, data)

            data = self.GetItem(index, col-3).GetText()
            wx.ListCtrl.SetStringItem(self, index, col-3, data[0:datalen])

    # def colorize(self):
    #     for idx in range(self.GetItemCount()):
    #         if idx % 2:
    #             self.SetItemBackgroundColour(idx, wx.Colour(200, 200, 200))
    #             # self.SetItemTextColour(idx, wx.Colour(0, 0, 0))
    #         else:
    #             # self.SetItemBackgroundColour(idx, wx.Colour(0, 0, 150))
    #             self.SetItemBackgroundColour(idx, wx.Colour(177, 177, 177))
    #             # self.SetItemTextColour(idx, wx.Colour(255, 255, 255))

    #     for idx, data in enumerate(temp_data):
    #         if data[1] == 1:
    #             # self.SetItemTextColour(idx, wx.Colour(255, 0, 0))
    #             if idx % 2 == 0:
    #                 self.SetItemBackgroundColour(idx, wx.Colour(255, 0, 0))
    #                 self.SetItemTextColour(idx, wx.Colour(255, 255, 255))
    #             else:
    #                 self.SetItemBackgroundColour(idx, wx.Colour(200, 0, 0))
    #                 self.SetItemTextColour(idx, wx.Colour(255, 255, 255))

    #         elif data[1] == 7:
    #             self.SetItemBackgroundColour(idx, wx.Colour(0, 200, 150))
    #             self.SetItemTextColour(idx, wx.Colour(0, 0, 0))

    def colorize(self):
        # for idx in range(self.GetItemCount()):
        #     if idx % 2:
        #         self.SetItemBackgroundColour(idx, wx.Colour(200, 200, 200))
        #         # self.SetItemTextColour(idx, wx.Colour(0, 0, 0))
        #     else:
        #         # self.SetItemBackgroundColour(idx, wx.Colour(0, 0, 150))
        #         self.SetItemBackgroundColour(idx, wx.Colour(177, 177, 177))
        #         # self.SetItemTextColour(idx, wx.Colour(255, 255, 255))

        for idx, data in enumerate(temp_data.get_as_list()):
            # if data[1] == 1:
            #     # self.SetItemTextColour(idx, wx.Colour(255, 0, 0))
            #     if idx % 2 == 0:
            #         self.SetItemBackgroundColour(idx, wx.Colour(255, 0, 0))
            #         self.SetItemTextColour(idx, wx.Colour(255, 255, 255))
            #     else:
            #         self.SetItemBackgroundColour(idx, wx.Colour(200, 0, 0))
            #         self.SetItemTextColour(idx, wx.Colour(255, 255, 255))

            # elif data[1] == 7:
            #     self.SetItemBackgroundColour(idx, wx.Colour(0, 200, 150))
            #     self.SetItemTextColour(idx, wx.Colour(0, 0, 0))

            fg = data.priority
            if idx % 2 == 0:
                self.SetItemBackgroundColour(idx, self._get_even_bg_color(fg))
                self.SetItemTextColour(idx, self._get_fg_color(fg))
            else:
                self.SetItemBackgroundColour(idx, self._get_odd_bg_color(fg))
                self.SetItemTextColour(idx, self._get_fg_color(fg))

    def _get_even_bg_color(self, i):
        return priority_colors[i][0][0]

    def _get_odd_bg_color(self, i):
        return priority_colors[i][0][1]

    def _get_fg_color(self, i):
        c = wx.Colour()
        if priority_colors[i][1] == 0:
            c = wx.Colour(255, 255, 255)
        elif priority_colors[i][1] == 1:
            c = wx.Colour(0, 0, 0)
        return c


class TodoListCtrlPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)

        # self.log = log
        tID = wx.NewId()

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.list = TodoListCtrl(self, tID,
                                style=wx.LC_REPORT
                                | wx.BORDER_NONE
                                | wx.LC_SORT_ASCENDING)

        # self.sizer.Add(self.list, 1, wx.EXPAND|wx.BORDER)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)

        # # Other useful bindings:
        # self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, self.list)
        # self.Bind(wx.EVT_LIST_DELETE_ITEM, self.OnItemDelete, self.list)
        # self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, self.list)
        # self.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.OnColRightClick, self.list)
        # self.Bind(wx.EVT_LIST_COL_BEGIN_DRAG, self.OnColBeginDrag, self.list)
        # self.Bind(wx.EVT_LIST_COL_DRAGGING, self.OnColDragging, self.list)
        # self.Bind(wx.EVT_LIST_COL_END_DRAG, self.OnColEndDrag, self.list)
        # self.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.OnBeginEdit, self.list)

    def get_listctr(self):
        return self.list

class TodoStatusBar(wx.StatusBar):
    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent, style=0)
        self.SetFieldsCount(1)
        # self.SetStatusStyles([1, wx.SB_FLAT])
        # self.SetFieldsCount(2)
        # self.SetStatusWidths([-2, -1])
        # self.sizeChanged = False
        # self.SetStatusText('Tasks: ', 0)
        # self.SetStatusText('INFO', 1)
        self.SetBackgroundColour(wx.Colour(50, 50, 50))
        # self.SetForegroundColour(wx.Colour(255, 77, 0))
        self.SetForegroundColour(wx.Colour(150, 150, 150))

        # for i in range(self.GetFieldsCount()):
        #     self.SetStatusStyles([i, wx.SB_FLAT])

        self.txt = wx.StaticText(self, wx.ID_ANY, 'INFO',
                                 wx.Point(10, 5), wx.DefaultSize, 0);

    def set_tasks(self, tasks):
        # self.SetStatusText('Tasks: ' + str(tasks))
        self.txt.Destroy()
        self.txt = wx.StaticText(self, wx.ID_ANY, 'Tasks: ' + str(tasks),
                                 wx.Point(100, 5), wx.DefaultSize, 0);
        # self.txt.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False,
        #                          u'Verdana'))
        self.Layout()


class TodoEditWindow(wx.Panel):
    def __init__(self, parent, display_list=False):
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)

        tID = wx.NewId()
        self.list = TodoListCtrl(self, tID,
                                style=wx.LC_REPORT
                                | wx.BORDER_NONE
                                | wx.LC_SORT_ASCENDING)
        self.list.Hide()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        # self.sizer.Add(wx.Button(self, 0, 'Test 1'), 0, wx.ALIGN_RIGHT|wx.ALL)
        # self.sizer.Add(wx.Button(self, 0, 'Test 2'), 0, wx.ALIGN_RIGHT|wx.ALL)

        # Display a second list / the same list
        if display_list:
            self.list.Show()
            self.sizer.Add(self.list, 1, wx.EXPAND|wx.ALL)
        self.SetBackgroundColour(wx.Colour(50, 50, 50))

        # # Calendar test
        # import wx.calendar as wxcal
        # self.calendar = wxcal.CalendarCtrl(self)
        # self.calendar.SetBackgroundColour('coral')
        # self.sizer.Add(self.calendar, 1, wx.EXPAND|wx.ALL)

        # # MVCTree test
        # import os
        # import wx.lib.mvctree as tree
        # self.mvc_tree = tree.MVCTree(self, -1)
        # self.mvc_tree.SetAssumeChildren(True)
        # self.mvc_tree.SetModel(tree.LateFSTreeModel(
        #         # os.path.normpath(os.getcwd() + os.sep + '...')))
        #         os.path.normpath(os.getenv('HOME'))))  # + os.sep + '...')))
        #         # os.path.normpath(os.getcwd())))  # + os.sep + '...')))
        # self.mvc_tree.SetBackgroundColour(wx.Colour(50, 50, 50))
        # self.mvc_tree.SetForegroundColour(wx.Colour(0, 255, 0))
        # self.mvc_tree.SetMultiSelect(True)
        # self.sizer.Add(self.mvc_tree, 1, wx.EXPAND|wx.ALL)

        # # VisualReport test
        # from visual_report import VisualReportPanel
        # self.visual_report = VisualReportPanel(self, data)
        # self.sizer.Add(self.visual_report, 1, wx.EXPAND|wx.ALL)

        self.Layout()

        self.Show()
