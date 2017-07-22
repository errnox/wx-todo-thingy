import wx
import cairo

import wx.lib.wxcairo


class VisualReport(wx.Frame):
    def __init__(self, parent=None, title='Report', data=None):
        wx.Frame.__init__(self, parent, title=title, size=(800, 500))
        self.main_panel = VisualReportPanel(self, data)

        self.box_sizer = wx.BoxSizer()

        self.box_sizer.Add(self.main_panel, 0, wx.ALIGN_LEFT|wx.ALL)
        self.main_panel.Layout()
        self.Show()


class VisualReportPanel(wx.ScrolledWindow):
    def __init__(self, parent, data):
        self.X_GAP = 15
        self.Y_GAP = 50
        self.data = data

        self.max_width = 2000
        self.max_height = 2000

        wx.ScrolledWindow.__init__(self, parent)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.SetVirtualSize((self.max_width, self.max_height))
        self.SetScrollRate(20, 20)

    def OnPaint(self, event):
        bfr = wx.EmptyBitmap(self.max_width, self.max_height)
        dc = wx.BufferedPaintDC(self, bfr, wx.BUFFER_VIRTUAL_AREA)
        dc.SetBackground(wx.Brush('white'))
        dc.Clear()
        self.Render(dc)
        # self.SaveDC(dc, bfr)

    def SaveDC(self, dc, bmp):
        memDC = wx.MemoryDC()
        memDC.SelectObject(bmp)
        memDC.Blit(0, 0, self.max_width, self.max_height, dc, 0, 0)
        memDC.SelectObject(wx.NullBitmap)
        img = bmp.ConvertToImage()
        img.SaveFile('output.png', wx.BITMAP_TYPE_PNG)

    def Render(self, dc):
        size = self.GetSize()
        dc.SetPen(wx.Pen('navy', 1))

        # # Draw diagonal lines
        # x = y = 0
        # while x < size.width * 2 or y <  size.height * 2:
        #     x += 20
        #     y += 10
        #     dc.DrawLine(x, 0, 0, y)

        c1 = c2 = c3 = c4 = c5 = c6 = c7 = 0

        for item in self.data.get_as_list():
            if item.priority == 1:
                c1 += 1
            elif item.priority == 2:
                c2 += 1
            elif item.priority == 3:
                c3 += 1
            elif item.priority == 4:
                c4 += 1
            elif item.priority == 5:
                c5 += 1
            elif item.priority == 6:
                c6 += 1
            elif item.priority == 7:
                c7 += 1

        counters = [c1, c2, c3, c4, c5, c6, c7, 8, 5, 3, 3, 40, 4, 5, 9, 3, 20, 10, 8, 7, 12]

        ctx = wx.lib.wxcairo.ContextFromDC(dc)
        ctx.set_line_width(25)
        ctx.select_font_face('Sans', cairo.FONT_SLANT_NORMAL,
                             cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(15)

        base_x = 20
        base_y = 20

        ctx.move_to(base_x, base_y)
        ctx.show_text('Priority')

        previous_x = base_x
        previous_y = base_y

        bmp = wx.Bitmap('res/images/go-next.png')
        img = wx.lib.wxcairo.ImageSurfaceFromBitmap(bmp)
        ctx.set_source_surface(img, 70, 230)
        ctx.paint()
        bmp2 = wx.lib.wxcairo.BitmapFromImageSurface(img)
        # dc.DrawBitmap(bmp2, 280, 300)

        for idx, counter in enumerate(counters):
            base_y += self.Y_GAP
            ctx.set_line_cap(cairo.LINE_CAP_BUTT)

            ctx.move_to(base_x + self.X_GAP, base_y + 5)
            ctx.set_source_rgba(0, 0, 0, 1)
            ctx.show_text(str(idx + 1))
            ctx.move_to(base_x + self.X_GAP, base_y)
            ctx.move_to(base_x + self.X_GAP * 3, base_y)
            ctx.line_to(counter * 20, base_y)

            ctx.set_source_rgba(0, 0, 0.5, 0.5)
            ctx.set_line_width(25)
            ctx.stroke()

            # ctx.curve_to(base_x + self.X_GAP * 3, base_y, base_y, counter, counter * 20, base_y)
            ctx.curve_to(max(counters) * 20 + 200, (len(counters) * self.Y_GAP) / 2,  # right
                         base_x * len(counters), base_y + len(counters),              # middle
                         counter * 20 + len(str(counter)) * 20 + self.X_GAP, base_y)  # left

            previous_x = base_x
            previous_y = base_y

            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.set_source_rgba(0.5, 0.5, 0.5, 0.5)
            ctx.set_line_width(3)
            ctx.stroke()

            ctx.move_to(counter * 20 + self.X_GAP/2, base_y + 5)
            ctx.set_source_rgba(0, 0, 0, 0.5)
            ctx.show_text('(' + str(counter) + ')')
            dc.DrawBitmap(bmp2, counter * 20 - self.X_GAP - 3, base_y - 7)

        ctx.move_to(max(counters) * 20 + 200 + 5, (len(counters) * self.Y_GAP) / 2 + 5)
        ctx.show_text('TASKS')

        ctx.set_source_rgba(0, 0, 0.5, 0.5)
        ctx.stroke()
