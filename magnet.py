# -*- coding: utf-8 -*-
__author__ = 'xdc'

from PyQt5 import QtCore, QtGui, QtWidgets

from dialog import Ui_Dialog

import requests
from bs4 import BeautifulSoup as bs
import os

global MAGNET_HEAD,SEARCH_URL,TRANS_URL
MAGNET_HEAD = 'magnet:?xt=urn:btih:'
SEARCH_URL = 'http://www.btaia.com/search/'
TRANS_URL = 'http://magnet.vuze.com/magnetLookup'


class Ui(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Ui, self).__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self) #inittial
        self.ui.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers) #read only
        self.ui.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)#单个选择
        self.ui.tableWidget.setAlternatingRowColors(1) #隔行显示颜色

        self.result = []


    def search(self):
        key = self.ui.lineEdit.text()
        if len(key)==40:
            #composite link
            link = MAGNET_HEAD+key
        else:
            handle = NetHandler()
            self.result=handle.getMagnetLink(key) #search from web
        #show in tableWidget
        j=0
        #debug
        '''for i in result:
            print type(i),i['hash']'''
        for i in self.result:
            self.ui.tableWidget.setItem(j,0,QtWidgets.QTableWidgetItem(MAGNET_HEAD+(self.result[j]['hash'])))
            self.ui.tableWidget.setItem(j,1,QtWidgets.QTableWidgetItem(self.result[j]['size']))
            self.ui.tableWidget.setItem(j,2,QtWidgets.QTableWidgetItem(self.result[j]['date']))
            j+=1
        #self.ui.tableWidget.resizeColumnsToContents()

    def currentRow(self):
        return 0 if self.ui.tableWidget.currentColumn() != 0 else self.ui.tableWidget.currentRow()

    def currenritem(self):
        return self.ui.tableWidget.item(0,0) if self.ui.tableWidget.currentColumn()!=0 else self.ui.tableWidget.currentItem()

    def copy(self):
         QtGui.QGuiApplication.clipboard().setText(self.currenritem().text())

    def download(self):
        key_hash = self.currenritem().text()[-40:]
        filePath = QtWidgets.QFileDialog.getSaveFileName(self,u"保存种子",self.result[self.currentRow()]['name'],"*.torrent") #*.torrent;; *.png;; *.jpg
        if filePath==None:
            return
        handle=NetHandler()
        handle.getTorrent(key_hash,filePath[0]+'.torrent')

     #status bar
    def showStatus(self):
        pass

    def bindEvent(self):
        #bind event
        self.ui.searchBtn.clicked.connect(self.search)
        self.ui.copyBtn.clicked.connect(self.copy)
        self.ui.downBtn.clicked.connect(self.download)

class MagNet(object):
    def __init__(self,_name,_hash,_size,_date):
        super(object,self).__init__()
        self._name = _name
        self._hash = _hash
        self._size = _size
        self._date = _date

    def downloadLink(self):
        return MAGNET_HEAD+self._hash

def singleeton(cls,*args,**kw):
    instances = {}
    def _singleton():
        if cls not in instances:
            instances[cls]=cls(*args,**kw)
        return instances[cls]
    return _singleton

#@singleeton
class NetHandler:
    def __init__(self):
        #super(object,self).__init__(parent)
        self.headers =  {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Language': 'zh_CN',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}

    def getMagnetLink(self,key):
        r = requests.get(SEARCH_URL+key,headers=self.headers)
        soup = bs(r.content,'lxml')
        #获取结果
        data_list = soup.find('div',class_='data-list')
        rows = data_list.find_all('div',class_='row')
        result=[]

        for i in rows[1:]:
            nameTag=i.div
            linkTag=i.a
            sizeTag=i.a.next_sibling.next_sibling
            dateTag=sizeTag.next_sibling.next_sibling #bs4有Bug,连跳2个才取到这个div节点，但它们明明是相邻兄弟
            data=dict()
            data['name'] = nameTag.get_text()
            data['hash'] = MAGNET_HEAD+linkTag['href'][-40:]
            data['size'] = sizeTag.string
            data['date'] = dateTag.string
            #result.extend(data) #wrong use
            result.append(data)
        return result

    def getTorrent(self,key_hash,filePath=None):
        hash = {'hash':key_hash.upper()}
        r = requests.get(TRANS_URL,params=hash)
        #headers=r.headers #get filename
        fp = open(filePath,'wb')
        fp.write(r.content)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.bindEvent()

    window.show()
    sys.exit(app.exec_())
