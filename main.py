from doctest import master
import tkinter
from turtle import bgcolor
from unicodedata import name
import customtkinter
from tkinter import CENTER, ttk
from sqlalchemy import column
import sv_ttk
import tkinter.font as tkFont
from tkinter import filedialog
import tkinter.messagebox as msgbox
from lib.tkVideoPlayer import TkinterVideo
import os
import core
import uuid
from tkinter import Menu
import time
import formatter
from PIL import Image, ImageTk
from functools import partial

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"
PATH = os.path.dirname(os.path.realpath(__file__))


def button_function():
    print("button pressed")

class App(customtkinter.CTk):
    WIDTH = 1080
    HEIGHT = 980

    def __init__(self):
        super().__init__()
        # =============== 组件 ===================
        self.DeleteIcon =  ImageTk.PhotoImage(Image.open(PATH + "/images/icon/delete.png").resize((16, 16), Image.ANTIALIAS))
        self.ChatIcon = ImageTk.PhotoImage(Image.open(PATH + "/images/icon/chat.png").resize((20, 20), Image.ANTIALIAS))
        self.ThemeIcon = ImageTk.PhotoImage(Image.open(PATH + "/images/icon/theme.png").resize((20, 20), Image.ANTIALIAS))

        # =============== 变量 ===================
        self.var_folder_path = tkinter.StringVar(value="请设置视频目录") 
        self.var_output_folder_path = tkinter.StringVar(value="请设置导出目录")         
        self.fileDict = {}
        self.playStatus = tkinter.StringVar(value="")
        self.progrssCurrentTime = tkinter.StringVar(value="0:00:00")
        self.progrssTotalTime = tkinter.StringVar(value="0:00:00")
        self.segmentTimePointList = []
        self.title("视频批量截取软件 v1.0")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  
        # ============ 绑定快捷键 =============
        self.bindShortCut()
        
        # ============ 左右两个分区 ============
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        self.frame_left = customtkinter.CTkFrame(master=self)
        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_left.grid(row=0, column=0, sticky="ns", padx=(20,10), pady=20)
        self.frame_left.grid_rowconfigure(3, weight=2)

        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=(0,20), pady=20)
        self.frame_right.grid_columnconfigure(0, weight=1)
        self.frame_right.grid_rowconfigure(2, weight=1)

        # ============ 右侧上中下三个分区 ============
        self.frame_right_top = customtkinter.CTkFrame(master=self.frame_right)
        self.frame_right_top.grid(row=0, column=0, pady=10, padx=10, sticky="nwse")
        self.frame_right_top.columnconfigure((0, 3), weight=1)
        self.frame_right_top.columnconfigure(2, weight=3)

                      
        self.frame_right_center = customtkinter.CTkFrame(master=self.frame_right)
        self.frame_right_center.grid(row=1, column=0, pady=10, padx=10,sticky="nsew")
        self.frame_right_center.grid_columnconfigure(0, weight=2)
        
        self.frame_right_bottom = ttk.PanedWindow(self.frame_right_center)
        self.frame_right_bottom.grid(row=3, column=0,columnspan=4, pady=10, padx=10, sticky="nsew", rowspan=1)

        # ==============  各个元素 ============
        # 左上角标题头
        self.brandLabel = customtkinter.CTkLabel(master=self.frame_left,
                                              text="视频批量剪辑",
                                              text_font=("优设标题黑", 16))  # font name and size in px
        self.brandLabel.grid(row=0, column=0, pady=10, padx=10,sticky="n")
        
        self.copyrightLabel = customtkinter.CTkLabel(master=self.frame_left,
                                              text="v0.1\n素语出品",
                                              text_font=("优设标题黑", 12))  # font name and size in px
        self.helpButton = customtkinter.CTkButton(master=self.frame_left,
                                                text="使用帮助",command=self.openHelpPage,text_font=("微软雅黑", 10),
                                                image=self.ChatIcon,height=36,corner_radius=6, fg_color="gray40", hover_color="gray25")
        
        self.themeButton = customtkinter.CTkButton(master=self.frame_left,
                                                text="切换主题",command=self.change_appearance_mode,text_font=("微软雅黑", 10),
                                                image=self.ThemeIcon, height=36,corner_radius=6, fg_color="gray40", hover_color="gray25")

        self.helpButton.grid(row=1, column=0, pady=20, padx=10,sticky="")
        self.themeButton.grid(row=2, column=0, pady=10, padx=10,sticky="")
        self.copyrightLabel.grid(row=4, column=0, pady=10, padx=10,sticky="")

        # ==============  右侧顶部 ============
        # 视频播放器
        self.videoplayerLabel = customtkinter.CTkLabel( master=self.frame_right_top,
                                                    text="未选择视频\n" +
                                                        "请在下方目录中选择视频",
                                                    height=340,
                                                    text_font=("微软雅黑", 10),
                                                    corner_radius=10,
                                                    fg_color=("white", "gray38"),  # <- custom tuple-color
                                                    justify=tkinter.CENTER)
        self.videoplayerLabel.grid(row=0, column=0, columnspan=4, pady=0, padx=0, sticky="nswe")
        self.videoplayer = TkinterVideo(master=self.videoplayerLabel,scaled=False)
        self.videoplayer.bind("<<Duration>>", self.playerUpdateDuration)
        self.videoplayer.bind("<<SecondChanged>>", self.updateScale)
        self.videoplayer.bind("<<Ended>>", self.videoEnded )

        self.videoplayer.grid(row=0, column=0, columnspan=4, pady=0, padx=0, sticky="nswe")
        
        # 控制区
        self.videoplayerPauseButton = customtkinter.CTkButton(master=self.frame_right_top,
                                                fg_color="#383838",
                                                textvariable=self.playStatus,
                                                command=self.pause_play)

        self.videoplayerImportButton = customtkinter.CTkButton(master=self.frame_right_top,
                                                fg_color="gray40",
                                                text="导入",                                            text_font=("微软雅黑", 10), width=120,

                                                command=self.importSingleVideo)

        self.singleVideoExportButton = customtkinter.CTkButton(master=self.frame_right_top,
                                                text="导出",                                            text_font=("微软雅黑", 10), width=120,

                                                fg_color="gray40",
                                                command=self.exportSingleVideo)
        self.speedOption = customtkinter.CTkOptionMenu(master=self.frame_right_top,
                                                        values=["1", "2", "0.1","0.5"],
                                                        command=self.changeVideoSpeed)
        # 添加分段信息
        self.frame_right_top_top = customtkinter.CTkFrame(master=self.frame_right_top,height=30,corner_radius=5)
        self.frame_right_top_top.grid(row=1, column=0, columnspan=4, pady=20, padx=20,sticky="we")
        self.videoplayerPauseButton.grid(row=2, column=1, columnspan=1, pady=10, padx=20, sticky="e")
        self.videoplayerImportButton.grid(row=2,column=2,columnspan=1, pady=10, padx=20, sticky="e")
        self.singleVideoExportButton.grid(row=2,column=3,columnspan=1, pady=10, padx=20, sticky="e")

        
        self.speedOption.grid(row=2, column=0, columnspan=1, pady=10, padx=20, sticky="w")

        # 左右进度文本
        self.progressLabelLeft = customtkinter.CTkLabel(master=self.frame_right_top,textvariable=self.progrssCurrentTime)
        self.progressLabelLeft.grid(row=3, column=0, columnspan=1, pady=10, padx=0, sticky="w")

        self.progressLabelRight = customtkinter.CTkLabel(master=self.frame_right_top,textvariable=self.progrssTotalTime)
        self.progressLabelRight.grid(row=3, column=3, columnspan=1, pady=10, padx=0, sticky="e")

        # 进度条
        self.videoSlider = customtkinter.CTkSlider(master=self.frame_right_top,
                                                from_=0,
                                                to=100,command=self.changeVideoProgress)
        self.videoSlider.set(0)                                                
        self.videoSlider.grid(row=3, column=1, columnspan=2, pady=10, padx=20, sticky="we")
        
        # ==============  右侧中间 ============

        self.scrollbar = ttk.Scrollbar(self.frame_right_bottom)
        self.scrollbar.pack( fill="both")

        self.treeview = ttk.Treeview(
            master=self.scrollbar,
            columns=("0","1","2"),
            height=10,
            selectmode="browse",
            show=("tree",)        ,
            yscrollcommand=self.scrollbar.set,
        )

        self.scrollbar.config(command=self.treeview.yview)

        # Treeview columns
        self.treeview.column(0, width=120,anchor=tkinter.CENTER)
        self.treeview.column(1, width=120,anchor=tkinter.CENTER)
        self.treeview.column(2, width=40,anchor=tkinter.CENTER)
        self.treeview.bind('<3>', self.popup)

        self.treeview.pack(expand=True, fill="both")

        fileList = [("", -1, "文件名", ("文件大小", "切割分数"))]

        # ==============  右侧底部 ============
        # 底部选择原始目录
        self.originFolderEntry = customtkinter.CTkEntry(master=self.frame_right_center,
                                            text_font=("微软雅黑", 10),
                                            textvariable=self.var_folder_path,
                                            placeholder_text="原始视频目录")

        self.outputFolderEntry = customtkinter.CTkEntry(master=self.frame_right_center,
                                            text_font=("微软雅黑", 10), width=120,
                                            textvariable=self.var_output_folder_path,
                                            placeholder_text="导出视频目录")
        
        self.progressbar = customtkinter.CTkProgressBar(master=self.frame_right_center)
        self.progressbar.set(0)

        self.selectOriginFolderButton = customtkinter.CTkButton(master=self.frame_right_center,                                            text_font=("微软雅黑", 10), width=120,

                                                text="选择文件夹",command=self.handleClickLoadFolderButton)

        self.selectOutputFolderButton = customtkinter.CTkButton(master=self.frame_right_center,                                            text_font=("微软雅黑", 10), width=120,

                                                text="选择文件夹",command=self.handleClickLoadOutputFolderButton)
        
        self.startProcessButton = customtkinter.CTkButton(master=self.frame_right_center,                                            text_font=("微软雅黑", 10), width=120,

                                                text="开始批量剪辑",command=self.handleClickStartProcessButton)

        self.originFolderEntry.grid(row=0, column=0,columnspan=2, pady=10, padx=20, sticky="we")
        self.outputFolderEntry.grid(row=1, column=0,columnspan=2, pady=10, padx=20, sticky="we")
        self.progressbar.grid(row=2, column=0, columnspan=2, pady=10, padx=20,sticky="we")

        self.selectOriginFolderButton.grid(row=0,  pady=10,  column=2, columnspan=1, padx=20,sticky="we")
        self.selectOutputFolderButton.grid(row=1,  pady=10,  column=2, columnspan=1, padx=20,sticky="we")
        self.startProcessButton.grid(row=2,  pady=10,  column=2, columnspan=1, padx=20,sticky="we")
    def openHelpPage(self):
        newWindow = tkinter.Toplevel(self)
        newWindow.geometry("400x600")
        newWindow.title("使用帮助")
        newWindow.iconphoto(False, tkinter.PhotoImage(file='./images/icon/logo.png'))
        newWindow.grid_columnconfigure(1,weight=1)
        label_1 = customtkinter.CTkLabel(master=newWindow,  height=40,corner_radius=10,
        text_font=("优设标题黑", 16),text="使用帮助")
        label_1.grid(row=0, column=0, columnspan=2,sticky="nwes", padx=(20,10), pady=(10,0))

        label_2 = customtkinter.CTkLabel(master=newWindow, height=40,corner_radius=10,width=200,anchor="w",
                                               fg_color=("gray70", "gray25"),text="1. 两种工作模式：批量与单个")

        label_3 = customtkinter.CTkLabel(master=newWindow, height=40,corner_radius=10,width=200,anchor="w",
                                               fg_color=("gray70", "gray25"),text="2. 文件名带有【0.1~0.2,0.4~0.6,0.7~0.9】，将自动解析")

        label_4 = customtkinter.CTkLabel(master=newWindow, height=40,corner_radius=10,width=200,anchor="w",
                                               fg_color=("gray70", "gray25"),text="3. 插入时间点的快捷键为k")                                                                                              
                                                                                              
        label_2.grid(row=1, column=0, columnspan=2,sticky="nwes", padx=(20,10), pady=10)
        label_3.grid(row=2, column=0, columnspan=2,sticky="nwes", padx=(20,10), pady=10)
        label_4.grid(row=3, column=0, columnspan=2,sticky="nwes", padx=(20,10), pady=10)
        
    def processDone(self,v):
        msgbox.showinfo("成功","切割成功")
        self.progressbar.set(1)

    def exportSingleVideo(self):
        if(len(self.segmentTimePointList)==0):
            msgbox.showerror("错误","没找到切割点")
            return
        if(self.videoplayer.path == ''):
            msgbox.showerror("错误","没选择视频")
        core.apply_ascyn(core.startProcessVideoByFileNameAndTimeList,(self.videoplayer.path,self.segmentTimePointList),callback=self.processDone)
        # core.startProcessVideoByFileNameAndTimeList(self.videoplayer.path,self.segmentTimePointList)

    def initSegmentButtonFromFileName(self,path):
        n=path.rfind("\\")#找到"\\"出现的位置
        fileName = path[n+1:] #输出为 class1.py
        parseFileNameResult = core.parseFileName(path,fileName)
        self.segmentTimePointList = []
        
        for index,point in enumerate(parseFileNameResult['timePartInfoArr']):
            self.segmentTimePointList.append({"name":str(uuid.uuid4()),"time":point[0]})
            self.segmentTimePointList.append({"name":str(uuid.uuid4()),"time":point[1]})
        print(self.segmentTimePointList)
        self.genSegmentButtonByList(self)

    def deleteSegmentButton(self,point):        
        name = point['name']
        self.frame_right_top_top.nametowidget(name).destroy()

        for item in self.segmentTimePointList:
            if(item['name'] == name):
                self.segmentTimePointList.remove(item)
                break

    def changeVideoProgress(self,val):
        if(self.videoplayer.path!=''):
            totalSeconds = self.videoplayer.video_info()["duration"]
            second = val*totalSeconds/100
            # 百分比转为秒 
            self.videoplayer.seek(int(second))
            self.progrssCurrentTime.set(formatter.seconds2Str(second))
    
    def importSingleVideo(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.initSegmentButtonFromFileName(file_path)        
            self.videoplayer.stop()
            self.videoplayer.load(file_path)
            self.videoplayer.seek(int(0))
            self.videoSlider.set(0)
            self.videoplayer.play()
            self.videoplayerPauseButton.configure(fg_color="#11b384")
            self.playStatus.set("暂停")

    def handleClickPlayItem(self,id):
        try:
            filePath = self.fileDict[id]['filePath']
            self.initSegmentButtonFromFileName(filePath)        
            self.videoplayer.stop()
            self.videoplayer.load(filePath)
            self.videoplayer.seek(int(0))
            self.videoSlider.set(0)
            self.videoplayer.play()
            self.videoplayerPauseButton.configure(fg_color="#11b384")
            self.playStatus.set("暂停")
        except Exception as e:
            msgbox.showinfo("提示",e)

    def videoEnded(self,val):
        print("播放完毕")
        self.playStatus.set("播放")

    def pause_play(self):
        if(self.videoplayer.path==''):
            file_path = filedialog.askopenfilename()
            if file_path:
                self.initSegmentButtonFromFileName(file_path)        
                self.videoplayer.stop()
                self.videoplayer.load(file_path)
                self.videoplayer.seek(int(0))
                self.videoSlider.set(0)
                self.videoplayer.play()
                self.playStatus.set("暂停")
                self.videoplayerPauseButton.configure(fg_color="#11b384",bg_color="red")
                return
            else:
                return
        """ pauses and plays """
        if self.videoplayer.is_paused():
            self.videoplayer.play()
            self.playStatus.set("暂停")
        else:
            self.videoplayer.pause()
            self.playStatus.set("播放")

    def bindShortCut(self):
        self.bind('<k>',self.addCutPoint)
        self.bind('<f>',self.playByFrame)


    # 逐帧播放
    def playByFrame(self):
        pass

    def clearAllSegmentButton(self,v):
        for widget in self.frame_right_top_top.winfo_children():
            widget.destroy()

    def genSegmentButtonByList(self,v=None):
        # 先清空
        self.clearAllSegmentButton(self)

        for index,point in enumerate(self.segmentTimePointList):
            tmpbtn = customtkinter.CTkButton(master=self.frame_right_top_top,compound="right", image=self.DeleteIcon, text=point['time'], width=50,
                            fg_color="gray40", hover_color="gray25",command= None,name=point['name'])
            if(index%2==0):
                tmpbtn.configure(text = "从："+point['time'], command= partial(self.deleteSegmentButton,point))
                tmpbtn.grid(row=0,column=index,padx=(0,6))
            else:
                tmpbtn.configure(text ="至："+ point['time'], command= partial(self.deleteSegmentButton,point))
                tmpbtn.grid(row=0,column=index,padx=(0,20))

    # 添加一个切割点
    def addCutPoint(self,event):
        print("event",event)
        timePoint = self.videoplayer.current_duration()
        name = str(uuid.uuid4())
        self.segmentTimePointList.append({"name":name,"time":"%.1fs" % (timePoint)})
        self.genSegmentButtonByList()

    def updateScale(self,val):
        currentSecond =  self.videoplayer.current_duration()
        totalSeconds = self.videoplayer.video_info()["duration"]
        self.progrssCurrentTime.set(formatter.seconds2Str(currentSecond))
        # 进度条做个映射
        self.videoSlider.set(100*currentSecond/totalSeconds)
    
        

    def playerUpdateDuration(self,event):
        totalSeconds = self.videoplayer.video_info()["duration"]
        self.progrssTotalTime.set(formatter.seconds2Str(totalSeconds))

        # end_time["text"] = str(datetime.timedelta(seconds=duration))

        # end_time["text"] = str(datetime.timedelta(seconds=duration))
        # progress_slider["to"] = duration

    def handleClickLoadOutputFolderButton(self):
        rootpath = filedialog.askdirectory()
        self.var_output_folder_path.set(rootpath)

    def handleClickStartProcessButton(self):
        if(self.var_output_folder_path.get() == r"请设置导出目录"):
            msgbox.showinfo("提示","请先选择输出路径")
        else:   
            core.apply_ascyn(core.startProcessVideo,(self.fileDict,self.var_output_folder_path.get()),callback=self.processDone)

    def changeVideoSpeed(self, speed):
        print(speed)

    def handleClickLoadFolderButton(self):
        fileCount = 0
        rootpath = filedialog.askdirectory()
        self.var_folder_path.set(rootpath)
        # 分析文件
        dirs = os.listdir(rootpath)

        fileList = [("", -1, "name", ("文件大小", "切割分数"))]

        self.fileDict = {}
        for i in self.treeview.get_children():
            self.treeview.delete(i)

        for index,fileName in enumerate(dirs):
            # 排除掉文件夹
            fullPath = rootpath+"/"+fileName
            if(not os.path.isfile(fullPath) or not core.isVideoFile(fileName)):
                continue
            fileCount = fileCount + 1
            # 根据文件名，切割分数
            parseResult = core.parseFileName(fullPath,fileName)         
            id = str(uuid.uuid4())
            fileList.append((-1, id, fileName, (core.getDocSize(fullPath), parseResult['partCount'])))
            if(len(parseResult['timePartInfoArr']))!=0:
                fileList.append((id, str(uuid.uuid4()), "分段序号", ("开始时间", "结束时间")))
                for index,part in enumerate(parseResult['timePartInfoArr']):
                    fileList.append((id,str(uuid.uuid4()),index+1,(part[0],part[1])))
            self.fileDict[id] = parseResult

        for item in fileList:
            parent, iid, text, values = item
            self.treeview.insert(
                parent=parent, index="end", iid=iid, text=text, values=values
            )
            self.treeview.item(iid, open=True)  
        # msgbox.showinfo("提示","找到"+str(fileCount)+"个视频文件")

    def on_closing(self, event=0):
        self.destroy()

    def change_appearance_mode(self):
        if(customtkinter.get_appearance_mode() == 'Light'):
            customtkinter.set_appearance_mode("Dark")
        else:
            customtkinter.set_appearance_mode("Light")
    
    # 右键事件
    def popup(self, event):
        iid = self.treeview.identify_row(event.y)        
        if (iid and iid!=-1 and iid in self.fileDict):        
            rcmenu = Menu(self.scrollbar, tearoff=0)
            rcmenu.add_command(label='删除',command =lambda : self.handleClickDeleteItem(iid))
            rcmenu.add_command(label='播放',command =lambda : self.handleClickPlayItem(iid))
            rcmenu.post(event.x_root, event.y_root)
        else:
            pass


if __name__ == '__main__':
    app = App()
    app.iconphoto(False, tkinter.PhotoImage(file='./images/icon/logo.png'))

    # 绑定快捷键
    # app.bind('<k>',sayHello )
    sv_ttk.set_theme("dark")
    # print(tkFont.families())#打印可选字体
    app.mainloop()
