import wx


class CompletionHtmlListBox(wx.HtmlListBox):
    items = None

    def OnGetItem(self, index):
        return self.items[index]


class CompletionPopup(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self,
                          parent, style=wx.FRAME_NO_TASKBAR|
                          wx.FRAME_FLOAT_ON_PARENT|wx.STAY_ON_TOP)
        self.html_list_box = CompletionHtmlListBox(self)
        self.html_list_box.SetItemCount(0)
        self.items_without_markup = []

    def SetSuggestions(self, suggestions):
        self.html_list_box.items = suggestions
        self.html_list_box.SetItemCount(len(suggestions))
        self.html_list_box.SetSelection(0)
        self.html_list_box.Refresh()

    def MoveUp(self):
        selected_item = self.html_list_box.GetSelection()
        if selected_item > 0:
            self.html_list_box.SetSelection(selected_item - 1)

    def MoveDown(self):
        selected_item = self.html_list_box.GetSelection()
        if selected_item < self.html_list_box.GetItemCount() - 1:
            self.html_list_box.SetSelection(selected_item + 1)

    def GetItem(self):
        return self.items_without_markup[self.html_list_box.GetSelection()]

    def GetItemAt(self, index):
        return self.html_list_box.items_without_markup[index]


class AutocompletionTextCtrl(wx.TextCtrl):
    def __init__(self, parent, suggestions=[], height=300, multiline=False):
        style = wx.TE_PROCESS_ENTER
        if multiline:
            style = style | wx.TE_MULTILINE

        wx.TextCtrl.__init__(self, parent, style=style)

        self.height = height

        self.frame = self.Parent
        while not isinstance(self.frame, wx.Frame):
            self.frame = self.frame.Parent

        self.delay = False
        self.switch = False

        self.suggestions = suggestions
        self.temp_suggestions = []
        self.completion_popup = CompletionPopup(self.frame)
        self.completion_popup.SetSuggestions(self.suggestions)

        self.frame.Bind(wx.EVT_MOVE, self.OnMove)
        self.Bind(wx.EVT_TEXT, self.OnText)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.completion_popup.html_list_box.Bind(wx.EVT_LEFT_DOWN,
                                                 self.OnSelect)
        self.completion_popup.html_list_box.Bind(wx.EVT_KEY_DOWN,
                                                 self.OnPopupKeyDown)

    def OnSize(self, event):
        self.completion_popup.Size = (self.Size[0], self.height)
        event.Skip()

    def SetPosition(self):
        # self.completion_popup.Postion = self.ClientToScreen((0, self.Size.height)).Get()
        self.completion_popup.SetPosition(self.ClientToScreen((0, self.Size.height)).Get())

    def OnMove(self, event):
        self.SetPosition()
        event.Skip()

    def SetSuggestions(self, suggestions):
        self.suggestions = suggestions

    def update_temp_suggestions(self, string=''):
        highlighted = '%s<u><b>%s</b></u>%s'
        self.temp_suggestions = []
        self.temp_suggestions = []
        self.completion_popup.items_without_markup = []
        for item in self.suggestions:
            if string in item:
                i = item.find(string)
                self.temp_suggestions.append(highlighted % (item[:i], string ,item[i+len(string):]))
                self.completion_popup.items_without_markup.append(item)

    def OnText(self, event):
        if self.delay:
            self.delay = False
        elif not self.switch:
            wx.CallLater(250, self.AutoComplete)
            self.switch = True

        event.Skip()

    def OnKeyDown(self, event):
        keycode = event.GetKeyCode()

        if keycode == wx.WXK_RETURN:
            self.skip_event = True
            self.SetValue(str(self.completion_popup.GetItem()))
            self.SetInsertionPointEnd()
            self.completion_popup.Hide()
            self.delay = True
        elif keycode == wx.WXK_UP:
            self.completion_popup.MoveUp()
        elif keycode == wx.WXK_DOWN:
            self.completion_popup.MoveDown()
        elif event.ControlDown() and unichr(keycode).lower() == 'a':
            self.SelectAll()
        elif keycode == wx.WXK_ESCAPE:
            self.completion_popup.Hide()

        event.Skip()

    def OnSelect(self, event):
        index = self.completion_popup.html_list_box.HitTest(event.Position)
        self.Value = self.completion_popup.GetItemAt(index)
        self.SetInsertionPointEnd()
        self.completion_popup.Hide()
        event.Skip()

    def OnPopupKeyDown(self, event):
        keycode = event.GetKeyCode()

        if keycode == wx.WXK_RETURN:
            self.delay = True
            self.SetValue(self.popup.GetSelectedSuggestion())
            self.InsertionPointEnd()
            self.completion_popup.Hide()
        elif not self.switch:
            self.switch = True

        event.Skip()

    def OnKillFocus(self, event):
        self.completion_popup.Hide()
        event.Skip()

    def AutoComplete(self):
        self.switch = False
        current = str(self.GetValue())
        self.temp_suggestions = []
        self.update_temp_suggestions(current)

        if self.Value != '' and not self.delay:
            if len(self.temp_suggestions) > 0:
                self.completion_popup.SetSuggestions(self.temp_suggestions)
                self.SetPosition()
                self.completion_popup.Show()
                self.SetFocus()
                self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
            else:
                self.completion_popup.Hide()
        else:
            self.completion_popup.Hide()


class TestFrame(wx.Frame):
    def __init__(self, title):
        wx.Frame.__init__(self, None, title=title, size=(350,200))
        self.main_panel = wx.Panel(self)
        self.box_sizer = wx.BoxSizer(wx.VERTICAL)
        self.suggestions = [
            'red',
            'redredred',
            'green',
            'blue',
            'violet',
            'pink',
            'brown',
            'white',
            'black'
            ]
        self.auto_complete_text_ctrl = AutocompletionTextCtrl(
            self, suggestions=self.suggestions)
        self.box_sizer.Add(self.auto_complete_text_ctrl)
        self.main_panel.SetSizer(self.box_sizer)
        self.main_panel.Layout()
        self.Show()


if __name__ == '__main__':
    app = wx.App()
    frame = TestFrame('Test')
    app.TopWindow = frame
    app.MainLoop()
