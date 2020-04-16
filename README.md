# Playlist_for_WALKMAN 
A40series他で利用できるプレイリスト作成GUI. 
# 機能 
__add_folder__  
選択したフォルダ以下に含まれる音声ファイルを探索してプレイリスト候補に追加.  
__add_file__  
選択した音声ファイルをプレイリスト候補に追加.  
___delete__  
候補のうち左クリックで選択した音源を候補から除外.  
__analyse__  
librosaを用いて簡易的にBPMを推定し,候補音源の平均BPMに近いものを解析済み音源の中からおすすめする.精度は正直よくない.  
__save__  
プレイリストを.m3uで出力.これをWALKMANの適切な場所にコピーすると,WALKMAN内でプレイリストが認識される.  
```
├ WALKMAN ─ MUSIC ───────
│           ├── playlist.m3u
│           │
│           ├── MUSICCLIP  
│           │   │       
│           │   ├── アルバムA  
│           │   │　　　 　　└── 音源.mp3  
│           │   │  
│           │   ├── アルバムB  
│           │   │　　 　　　└── 音源2.flac  
│           │   │　  
```  
__Drag and Drop__  
フレーム内にフォルダorファイルをDnDすると,`add_file`or`add_folder`の挙動をする.  
__shift+leftclick(or UpDown button)__  
ある音源からクリックした音源までを連続して全選択.  
__ctrl+shift+leftclick__  
複数選択した音源のうち,クリックしたものだけ選択解除.  
__titleColumn__  
左クリックで音源を辞書順にソート.  

