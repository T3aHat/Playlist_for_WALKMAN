from pathlib import Path
import os
import wx
import sys
import pydub as dub
from pydub.playback import play
import shutil
import tempfile as temp
import librosa
import csv
extensions={
    ".mp3",".flac",".wav",".m4a"
}

def isMedia(p):
    return p.suffix in extensions

def rec_file_search(path):
    if os.path.isdir(path):
        files=os.listdir(path)
        for file in files:
            rec_file_search(path+"/"+file)
    else:
        p=Path(path)
        if isMedia(p):
            abs_pathlist.append(path)
            pathlist.append(path.split("MUSIC/")[1])
            titlelist.append(p.stem)
    
    
def sort_list(titlelist,pathlist):
    templist=list(zip(titlelist,pathlist))
    templist2=list(zip(titlelist,abs_pathlist))
    templist.sort()
    templist2.sort()
    for i in range(len(templist)):
        titlelist[i]=templist[i][0]
        pathlist[i]=templist[i][1]
        abs_pathlist[i]=templist2[i][1]

        
def add_songs2(abs_path):
    rec_file_search(abs_path)


def bpm_analyse(abs_path):
    p=Path(abs_path)
    title=p.stem
    print(title)
    print(abs_path)
    y,sr=librosa.load(abs_path,duration=50)
    y_harm, y_perc = librosa.effects.hpss(y, margin=1.5)
    librosa.output.write_wav('tmp_perc.wav', y_perc, sr)
    y,sr=librosa.load("path_to_tmp_perc.wav",duration=50)
    onset_env = librosa.onset.onset_strength(y, sr=sr)
    tempo = int(librosa.beat.tempo(onset_envelope=onset_env, sr=sr))
    print("tempo= "+str(tempo))
    return title,abs_path,tempo
    

def get_reclist(datalist,titlelist_isin_datalist):
    reclist=[]
    avgbpm=0
    for title in titlelist:
        avgbpm+=int(datalist[titlelist_isin_datalist.index(title)][2])/len(titlelist)
    print(avgbpm)
    for data in datalist:
        tempbpm=datalist[datalist.index(data)][2]
        print("tempbpm="+str(tempbpm))
        print(datalist[datalist.index(data)][0])
        if(abs(int(avgbpm)-int(tempbpm))<=30 and datalist[datalist.index(data)][0] not in titlelist):
            reclist.append(data)
    print(reclist)
    return reclist,avgbpm


    
class App(wx.Frame):
    def __init__(self,parent,id,title):
        wx.Frame.__init__(self, parent, id, title, size=(1200, 800), style=wx.DEFAULT_FRAME_STYLE)
        
        p = wx.Panel(self, wx.ID_ANY)
        self.listctrl = wx.ListCtrl(p, wx.ID_ANY, style=wx.LC_REPORT)
        self.listctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.item_select)
        self.listctrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.item_select)#select時とやるべきことは同じ
        self.listctrl.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.delete)
        self.listctrl.Bind(wx.EVT_LIST_COL_CLICK,self.col_sort_list)
        self.listctrl.InsertColumn(0,"title",wx.LIST_FORMAT_LEFT,300)
        self.listctrl.InsertColumn(1,"path",wx.LIST_FORMAT_LEFT,1500)
        
        for i in range(len(titlelist)):
            print("No."+str(i)+" "+str(titlelist[i]))
            self.listctrl.InsertItem(i,titlelist[i])
            self.listctrl.SetItem(i,1,pathlist[i])
            
        self.dltbtn=wx.Button(p,label="delete",size=(100,50))
        self.dltbtn.Bind(wx.EVT_BUTTON,self.delete)
        self.savebtn=wx.Button(p,label="save",size=(200,50))
        self.savebtn.Bind(wx.EVT_BUTTON,self.save)
        self.addbtn=wx.Button(p,label="add_folder",size=(100,50))
        self.addbtn.Bind(wx.EVT_BUTTON,self.add)
        self.add_filebtn=wx.Button(p,label="add_file",size=(100,50))
        self.add_filebtn.Bind(wx.EVT_BUTTON,self.add_file)
        self.anlsbtn=wx.Button(p,label="analyse",size=(100,50))
        self.anlsbtn.Bind(wx.EVT_BUTTON,self.analyse)
        
        layout=wx.BoxSizer(wx.HORIZONTAL)
        layout2=wx.BoxSizer(wx.VERTICAL)
        layout3=wx.BoxSizer(wx.VERTICAL)
        #layout2=wx.BoxSizer(wx.VERTICAL)
        layout.Add(self.listctrl,1,wx.GROW)
        layout2.Add(self.addbtn,0.1,wx.BOTTOM,border=10)
        layout2.Add(self.add_filebtn,0.1,wx.BOTTOM,border=10)
        layout2.Add(self.dltbtn,0.1,wx.BOTTOM,border=10)
        layout2.Add(self.anlsbtn,1,wx.TOP,border=30)
        layout.Add(layout2)
        layout3.Add(layout,wx.EXPAND)
        layout3.Add(self.savebtn,1,wx.ALIGN_RIGHT)
        p.SetSizer(layout3)

        self.Show()
       
        
    def item_select(self, event):#update self.indexlist
        print("item_select")
        self.select_indexlist=[]
        item=-1
        while 1:
            item = self.listctrl.GetNextItem(item,wx.LIST_NEXT_ALL,wx.LIST_STATE_SELECTED)
            if item != -1:
                self.select_indexlist.append(item)
            else:
                break
        print(self.select_indexlist)
        
    
    def delete(self,event):
        for select_index in self.select_indexlist:
            print("delete "+str(titlelist[select_index]))
            titlelist.pop(select_index)
            pathlist.pop(select_index)
            abs_pathlist.pop(select_index)
            
            self.listctrl.DeleteItem(select_index)
            for i in range(self.select_indexlist.index(select_index),len(self.select_indexlist)):
                self.select_indexlist[i]-=1
        self.select_indexlist=[]#delete終わったなら消せ

    def add(self,event):
        folder = wx.DirDialog(self, style=wx.DD_CHANGE_DIR,
                              message="Select a directory")
        if folder.ShowModal() == wx.ID_OK:
            abs_path = folder.GetPath()
            print(abs_path)
            folder.Destroy()
            add_songs2(abs_path)
            self.listctrl.DeleteAllItems()
            for i in range(len(titlelist)):
                print("No."+str(i)+" "+str(titlelist[i]))
                self.listctrl.InsertItem(i,titlelist[i])
                self.listctrl.SetItem(i,1,pathlist[i])
      

    def add_file(self,event):
        file = wx.FileDialog(self, style=wx.DD_CHANGE_DIR,
                              message="Select a file")
        if file.ShowModal() == wx.ID_OK:
            abs_path = file.GetPath()
            print(abs_path)
            file.Destroy()
            add_songs2(abs_path)
            self.listctrl.DeleteAllItems()
            for i in range(len(titlelist)):
                print("No."+str(i)+" "+str(titlelist[i]))
                self.listctrl.InsertItem(i,titlelist[i])
                self.listctrl.SetItem(i,1,pathlist[i])
            

    def col_sort_list(self,event):
        sort_list(titlelist,pathlist)
        print(titlelist)
        self.listctrl.DeleteAllItems()
        for i in range(len(titlelist)):
            print("No."+str(i)+" "+str(titlelist[i]))
            self.listctrl.InsertItem(i,titlelist[i])
            self.listctrl.SetItem(i,1,pathlist[i])

            
    def save(self, event):
        with wx.FileDialog(self, "Save playlist", wildcard="M3U files (*.m3u)|*.m3u",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'w') as f:
                    f.writelines("\n".join(pathlist))
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)

    def analyse(self,event):#(path,bpm)
        print("analyse()")
        datalist=[]
        try:
            with open("path_to_datalist.csv","r")as f:
                reader=csv.reader(f)
                for r in reader:
                    datalist.append(r)
        except:
            print("datalist.csvを読み込めませんでした")
        print("datalist.csvから以下の曲情報のcacheを取得しました")
        print(datalist)

        titlelist_isin_datalist=[]
        for i in range(len(datalist)):
            print(datalist[i][0])
            titlelist_isin_datalist.append(datalist[i][0])
        print(titlelist_isin_datalist)
        
        bpm_list=[]
        changed=False#IO減らすため.なくても正常に動く
        for abs_path in abs_pathlist:
            title=Path(abs_path).stem
            if(title not in titlelist_isin_datalist):
                print(str(title)+":なかったから解析する")
                analysedata=bpm_analyse(abs_path)
                bpm_list.append(analysedata)
                datalist.append(analysedata)
                titlelist_isin_datalist.append(datalist[-1][0])#怪しい
                print(bpm_list)
                changed=True
            else:
                print(str(title)+":あったで")
        if changed:
            with open("path_to_datalist.csv","a")as f:
                writer=csv.writer(f,lineterminator="\n")
                writer.writerows(bpm_list)
            print("update datalist.csv")
            
        print(datalist)
        
        get_reclistdata=get_reclist(datalist,titlelist_isin_datalist)
        self.reclist=get_reclistdata[0]
        self.avgbpm=get_reclistdata[1]
        box=Dialog(self,self.reclist,self.listctrl,self.avgbpm)
        ans=box.ShowModal()
     

        
class Dialog(wx.Dialog):
    def __init__(self,parent,reclist,listctrl,avgbpm):
        wx.Dialog.__init__(self,parent,-1,"Reccomend for average BPM="+str(int(avgbpm)),size=(800,600),style=wx.DEFAULT_DIALOG_STYLE)
        self.reclist2=reclist
        print(self.reclist2)
        self.listctrl2=listctrl
        self.rectitlelist=[]
        self.recbpmlist=[]
        for rec in reclist:
            self.rectitlelist.append(rec[0])
            self.recbpmlist.append(rec[2])
        print(self.rectitlelist)
        print(self.recbpmlist)
            
        self.dialistctrl = wx.ListCtrl(self,style=wx.LC_REPORT)
        self.dialistctrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.item_select)
        self.dialistctrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.item_select)
        self.dialistctrl.Bind(wx.EVT_LIST_COL_CLICK,self.sort_list_by_bpm)
        self.dialistctrl.InsertColumn(0,"TITLE",wx.LIST_FORMAT_LEFT,400)
        self.dialistctrl.InsertColumn(1,"BPM",wx.LIST_FORMAT_LEFT,100)

        for i in range(len(self.rectitlelist)):
            print("dialog_No."+str(i)+" "+str(self.rectitlelist[i]))
            self.dialistctrl.InsertItem(i,self.rectitlelist[i])
            self.dialistctrl.SetItem(i,1,self.recbpmlist[i])

        self.addbtn=wx.Button(self,label="add",size=(100,50))
        self.addbtn.Bind(wx.EVT_BUTTON,self.add)
            
        dialo = wx.BoxSizer(wx.VERTICAL)
        dialo.Add(self.dialistctrl,1,wx.EXPAND)
        dialo.Add(self.addbtn)
        self.SetSizer(dialo)
        self.Show()

        
    def item_select(self,event):
        self.select_indexlist=[]
        item = -1
        while 1:
            item = self.dialistctrl.GetNextItem(item,wx.LIST_NEXT_ALL,wx.LIST_STATE_SELECTED)
            if item != -1:
                self.select_indexlist.append(item)
            else:
                break
        print("select_indexlist of item_select")
        print(self.select_indexlist)

        
    def add(self,event):
        for select_index in self.select_indexlist:
            print("Add "+str(self.reclist2[select_index]))
            titlelist.append(self.reclist2[select_index][0])
            print(titlelist)
            pathlist.append(self.reclist2[select_index][1].split("MUSIC/")[1])
            abs_pathlist.append(self.reclist2[select_index][1])
            self.listctrl2.DeleteAllItems()
            for i in range(len(titlelist)):
                print("No."+str(i)+" "+str(titlelist[i]))
                self.listctrl2.InsertItem(i,titlelist[i])
                self.listctrl2.SetItem(i,1,pathlist[i])
            self.reclist2.pop(select_index)
            self.rectitlelist.pop(select_index)
            self.recbpmlist.pop(select_index)
            self.dialistctrl.DeleteItem(select_index)
            for i in range(self.select_indexlist.index(select_index),len(self.select_indexlist)):
                self.select_indexlist[i]-=1
        self.select_indexlist=[]#delete終わったなら消せ

        
    def sort_list_by_bpm(self,event):
        bpm=lambda val: int(val[1])
        templist=list(zip(self.rectitlelist,self.recbpmlist))
        templist.sort(key=bpm)
        for i in range(len(templist)):
            self.rectitlelist[i]=templist[i][0]
            self.recbpmlist[i]=templist[i][1]
        self.dialistctrl.DeleteAllItems()
        for i in range(len(self.rectitlelist)):
            print("dialog_No."+str(i)+" "+str(self.rectitlelist[i]))
            self.dialistctrl.InsertItem(i,self.rectitlelist[i])
            self.dialistctrl.SetItem(i,1,self.recbpmlist[i])
        

            
if __name__ == '__main__':
    abs_pathlist=[]
    pathlist=[]
    titlelist=[]
    plist=[]
    select_indexlist=[]
    reclist=[]

    app=wx.App()
    App(None,wx.ID_ANY,"wasshoi")
    app.MainLoop()



    
