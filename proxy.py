# -*- coding: utf-8 -*-

import urllib2,time,random,re,threading,string,sys,urllib,urllib2,getopt
import MySQLdb,socks,socket
import BeautifulSoup

web_site_count=13   #要抓取的网站数目
indebug=1        

thread_num=200                   # 开 thread_num 个线程检查代理
check_in_one_call=thread_num*10  # 本次程序运行时 最多检查的代理个数

db_host='localhost' # 数据库设置
db_port=3306
db_user='root'
db_passwd='123'
db_database='social'
db_charset='utf8'

target_url="http://www.baidu.com/"   # 验证代理的时候通过代理访问这个地址
target_string="030173"               # 如果返回的html中包含这个字符串，
target_timeout=10                    # 并且响应时间小于 target_timeout 秒 
                                     #那么我们就认为这个代理是有效的 
                                     
proxy_use=1   #抓取时，是否使用代理
proxy_ip='127.0.0.1'
proxy_port='8087'

proxy_array=[]          # 这个数组保存将要添加到数据库的代理列表 
update_array=[]         # 这个数组保存将要更新的代理的数据 

conn=None                 #数据库全局对象
cursor=None

def  usage():
  print u"-h help"
  print u"-g 抓取所有的网站代理"
  print u"-c http-普通http代理 connect-支持connect代理 检查代理"
  print u"-t id  测试抓取指定id的网站代理，不入库"

def get_html(url=''):
    if proxy_use==1:
      opener = urllib.FancyURLopener({'http': 'http://'+proxy_ip+':'+proxy_port+'/'})
    else:
      opener = urllib.FancyURLopener({})
    opener.addheaders = [('User-agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.76 Safari/537.36')]
    try:
      f = opener.open(url)
      return f.read()
    except Exception,e:
      print e
      return ''	

def build_list_urls_1(page=10):
	page=page+1
	ret=[]
	for i in range(1,page):
		ret.append('http://www.cnproxy.com/proxy%(num)01d.html'%{'num':i})		
	return ret

def parse_page_1(html=''):
	matches=re.findall('<tr><td>(.*?)<script.*?>document.write\(\":\"\+(.*?)\)</script></td><td>(.*?)</td><td>.*?</td><td>(.*?)</td>',html,re.IGNORECASE)	  
	ret=[]
	for match in matches:
		ip=match[0]
		port=match[1]	
		v="3";m="4";a="2";l="9";q="0";b="5";i="7";w="6";r="8";c="1";	
		portlist=port.split('+')
		porttmp=''
		for intstr in portlist:
		  porttmp=porttmp+eval(intstr)
		port=porttmp
		method=match[2]
		if method=='HTTP':
		  method=1
		elif method=='SOCKS4':
		  method=2
		elif method=='SOCKS5':
		  method=3
		type=-1          #该网站未提供代理服务器类型
		area=match[3]
		if indebug:
		  print '1',ip,port,method,type,area
		area=unicode(area, 'cp936')
		area=area.encode('utf8')
		ret.append([ip,port,method,type,area])
	return ret

def build_list_urls_2(page=1):
	return ['http://www.proxylists.net/http_highanon.txt']

def parse_page_2(html=''):
  matches=re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\:(\d{2,5})',html)
  ret=[]
  for match in matches:
		ip=match[0]
		port=match[1]
		method=1
		type=2         
		area='--'
		ret.append([ip,port,method,type,area])
		if indebug:
		  print '2',ip,port,method,type,area
  return ret


def build_list_urls_3(page=1):
	return ['http://www.proxylists.net/http.txt']

def parse_page_3(html=''):
  matches=re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\:(\d{2,5})',html)
  ret=[]
  for match in matches:
		ip=match[0]
		port=match[1]
		method=1
		type=-1         
		area='--'
		ret.append([ip,port,method,type,area])
		if indebug:
		  print '3',ip,port,method,type,area
  return ret



def build_list_urls_4(page=5):
	page=page+1
	ret=[]
	for i in range(0,page):
		ret.append('http://proxylist.sakura.ne.jp/index.htm?pages=%(n)01d'%{'n':i})		
	return ret

def parse_page_4(html=''):
  matches=re.findall('<TD.*?>[\s\S]*?<script.*?>[\s\S]*?proxy\((.*?)\);[\s\S]*?<\/script>[\s\S]*?<\/TD>[\s\S]*?<TD>(.*?)<\/TD>[\s\S]*?',html,re.IGNORECASE)
  ret=[]
  for match in matches:
		ipandport=match[0]
		ipandportlist=ipandport.split(',')
		port=ipandportlist[5]
		if ipandportlist[0]=='1':
		  ip=ipandportlist[1].strip("'")+"."+ipandportlist[2].strip("'")+"."+ipandportlist[3].strip("'")+"."+ipandportlist[4].strip("'")
		elif ipandportlist[0]=='2':
		  ip=ipandportlist[4].strip("'")+"."+ipandportlist[1].strip("'")+"."+ipandportlist[2].strip("'")+"."+ipandportlist[3].strip("'")
		elif ipandportlist[0]=='3':
		  ip=ipandportlist[3].strip("'")+"."+ipandportlist[4].strip("'")+"."+ipandportlist[1].strip("'")+"."+ipandportlist[2].strip("'")
		elif ipandportlist[0]=='4': 
		  ip=ipandportlist[2].strip("'")+"."+ipandportlist[3].strip("'")+"."+ipandportlist[4].strip("'")+"."+ipandportlist[1].strip("'") 
		method=1
		type=-1         
		area=match[1]
		if (type=='Anonymous'):
		  type=1
		else:
		  type=-1
		ret.append([ip,port,method,type,area])
		if indebug:
		  print '4',ip,port,method,type,area
  return ret

def build_list_urls_5(page=10):
	page=page+1
	ret=[]
	for i in range(1,page):
	  ret.append('http://www.my-proxy.com/free-proxy-list-%(n)01d.html'%{'n':i})
	ret.append('http://www.my-proxy.com/free-proxy-list-s1.html')
	ret.append('http://www.my-proxy.com/free-proxy-list-s2.html')
	ret.append('http://www.my-proxy.com/free-proxy-list-s3.html')
	return ret

def parse_page_5(html=''):
  matches=re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\:(\d{2,5})',html)
  ret=[]
  method=1
  type=-1
  for match in matches:
		ip=match[0]
		port=match[1]
		area='--'        
		ret.append([ip,port,method,type,area])
		if indebug:
		  print '5',ip,port,method,type,area
  return ret

def build_list_urls_6(page=4):
  ret=[]
  ret.append('http://www.cybersyndrome.net/plr5.html')
  ret.append('http://www.cybersyndrome.net/pla5.html')
  ret.append('http://www.cybersyndrome.net/pld5.html')
  return ret

def parse_page_6(html=''):
  matches=re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\:(\d{2,5})',html)
  ret=[]
  for match in matches:
		ip=match[0]
		port=match[1]
		method=1
		area='--'
		type=-1
		ret.append([ip,port,method,type,area])
		if indebug:
		  print '6',ip,port,method,type,area
  return ret



def build_list_urls_7(page=3):
    ret=[]
    ret.append('http://cn-proxy.com/')
    return ret

def parse_page_7(html=''):
    ret=[]
    matches=re.findall('<tr>[\s\S]*?<td>(.*?)</td>[\s\S]*?<td>(.*?)</td>[\s\S]*?<td>(.*?)</td>[\s\S]*?</tr>',html,re.IGNORECASE)	
    for match in matches:
      ip=match[0]
      port=match[1]
      method=1
      type=-1
      area=match[2]
      ipmatch=re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',ip)
      if len(ipmatch)>0:
        ret.append([ip,port,method,type,area])
        if indebug:
          print '7',ip,port,method,type,area.decode('utf8')
    return ret
    
def build_list_urls_8(page=3):
    ret=[]
    ret.append('http://cn-proxy.com/archives/218')
    return ret

def parse_page_8(html=''):
    ret=[]
    matches=re.findall('<tr>[\s\S]*?<td>(.*?)</td>[\s\S]*?<td>(.*?)</td>[\s\S]*?<td>(.*?)</td>[\s\S]*?<td>(.*?)</td>[\s\S]*?</tr>',html,re.IGNORECASE)	
    for match in matches:
      ip=match[0]
      port=match[1]
      method=1
      type=match[2].decode('utf8')
      if type==u'透明':
        type=0
      elif type==u'普通匿名':
        type=1
      elif type==u'高度匿名':
        type=2
      else:
        type=-1
      area=match[3]
      ipmatch=re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',ip)
      if len(ipmatch)>0:
        ret.append([ip,port,method,type,area])
        if indebug:
          print '8',ip,port,method,type,area.decode('utf8')
    return ret
    
def build_list_urls_9(page=4):
  ret=[]
  rehtml=get_html("http://www.youdaili.cn/Daili/http/")
  soup=BeautifulSoup(rehtml,from_encoding='utf-8')
  urllist=soup.find_all('ul','newslist_line')[0].find_all('li')
  for url in urllist:
    ret.append(url.find_all('a')[0]['href'])
  rehtml=get_html("http://www.youdaili.cn/Daili/QQ/")
  soup=BeautifulSoup(rehtml,from_encoding='utf-8')
  urllist=soup.find_all('ul','newslist_line')[0].find_all('li')
  for url in urllist:
    ret.append(url.find_all('a')[0]['href'])
  rehtml=get_html("http://www.youdaili.cn/Daili/guonei/")
  soup=BeautifulSoup(rehtml,from_encoding='utf-8')
  urllist=soup.find_all('ul','newslist_line')[0].find_all('li')
  for url in urllist:
    ret.append(url.find_all('a')[0]['href'])
  rehtml=get_html("http://www.youdaili.cn/Daili/guowai/")
  soup=BeautifulSoup(rehtml,from_encoding='utf-8')
  urllist=soup.find_all('ul','newslist_line')[0].find_all('li')
  for url in urllist:
    ret.append(url.find_all('a')[0]['href'])
  rehtml=get_html("http://www.youdaili.cn/Daili/Socks/")
  soup=BeautifulSoup(rehtml,from_encoding='utf-8')
  urllist=soup.find_all('ul','newslist_line')[0].find_all('li')
  for url in urllist:
    ret.append(url.find_all('a')[0]['href'])
  return ret

def parse_page_9(html=''):
  matches=re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\:(\d{2,5})\@(.*?)\#(.*?)<br \/>',html)
  ret=[]
  for match in matches:
		ip=match[0]
		port=match[1]
		method=match[2]
		if method=='HTTP':
		  method=1
		elif method=='SOCKS4':
		  method=2
		elif method=='SOCKS5':
		  method=3
		else:
		  continue
		area=match[3]
		type=-1
		ret.append([ip,port,method,type,area])
		if indebug:
		  print '9',ip,port,method,type,area.decode('utf8')
  return ret
  
def build_list_urls_10(page=4):
  ret=[]
  rehtml=get_html("http://www.itmop.com/proxy/")
  soup=BeautifulSoup(rehtml,from_encoding='utf-8')
  urllist=soup.find_all('dt')
  for url in urllist:
    ret.append(url.find_all('a')[0]['href'])
  return ret

def parse_page_10(html=''):
  matches=re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\:(\d{2,5})\@(.*?)\;(.*?)<br \/>',html)
  ret=[]
  for match in matches:
		ip=match[0]
		port=match[1]
		method=match[2]
		if method=='HTTP':
		  method=1
		elif method=='SOCKS4':
		  method=2
		elif method=='SOCKS5':
		  method=3
		else:
		  continue
		area=match[3]
		type=-1
		ret.append([ip,port,method,type,area])
		if indebug:
		  print '10',ip,port,method,type,area.decode('utf8')
  return ret
  
def build_list_urls_11(page=4):
  ret=[]
  ret.append('http://pachong.org/')
  ret.append('http://pachong.org/anonymous.html')
  ret.append('http://pachong.org/transparent.html')
  ret.append('http://pachong.org/area/short/name/cn.html')
  ret.append('http://pachong.org/area/short/name/br.html')
  ret.append('http://pachong.org/area/short/name/us.html')
  ret.append('http://pachong.org/area/short/name/ve.html')
  ret.append('http://pachong.org/area/short/name/in.html')
  return ret

def parse_page_11(html=''):
  matches=re.findall('<tr.*?data-type=\"(.*?)\">[\s\S]*?<td.*?>.*?</td>[\s\S]*?<td>(.*?)</td>[\s\S]*?<td>(.*?)</td>[\s\S]*?<td>[\s\S]*?<img.*?>[\s\S]*?<a.*?>(.*?)</a>',html,re.IGNORECASE)
  ret=[]
  for match in matches:
		ip=match[1]
		port=match[2]
		method=1
		area=match[3]
		type=match[0]
		if type=='anonymous':
		  type=1
		elif type=='transparent':
		  type=0
		elif type=='high':
		  type=2
		elif type=='socks4':
		  method=2
		  type=-1
		elif type=='socks5':
		  method=3
		  type=-1
		else:
		  type=-1
		ret.append([ip,port,method,type,area])
		if indebug:
		  print '11',ip,port,method,type,area.decode('utf8')
  return ret

def build_list_urls_12(page=10):
  ret=[]
  ret.append('http://www.cz88.net/proxy/index.aspx')
  page=page+1
  for i in range(2,page):
	  ret.append('http://www.cz88.net/proxy/http_%(n)01d.aspx'%{'n':i})
  return ret

def parse_page_12(html=''):
  matches=re.findall('<tr><td>(.*?)</td><td>(.*?)</td><td>.*?</td><td>.*?</td><td><div.*?>(.*?)</div></td></tr>',html,re.IGNORECASE)
  ret=[]
  for match in matches:
		ip=match[0].decode('gbk').encode('utf8')
		port=match[1].decode('gbk').encode('utf8')
		method=1
		area=match[2].decode('gbk').encode('utf8')
		type=-1
		ret.append([ip,port,method,type,area])
		if indebug:
		  print '12',ip,port,method,type,area.decode('utf8')
  return ret
  
def build_list_urls_13(page=10):
  ret=[]
  ret.append('http://www.cz88.net/proxy/socks4.aspx')
  ret.append('http://www.cz88.net/proxy/socks4_2.aspx')
  ret.append('http://www.cz88.net/proxy/socks4_3.aspx')
  ret.append('http://www.cz88.net/proxy/socks5.aspx')
  ret.append('http://www.cz88.net/proxy/socks5_2.aspx')
  return ret

def parse_page_13(html=''):
  matches=re.findall('<tr><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>.*?</td><td><div.*?>(.*?)</div></td></tr>',html,re.IGNORECASE)
  ret=[]
  for match in matches:
		ip=match[0].decode('gbk').encode('utf8')
		port=match[1].decode('gbk').encode('utf8')
		method=match[2].decode('gbk').encode('utf8')
		if method.decode('utf8')==u'SOCKS4':
		  method=2
		elif method.decode('utf8')==u'SOCKS5':
		  method=3
		else:
		  continue
		area=match[3].decode('gbk').encode('utf8')
		type=-1
		ret.append([ip,port,method,type,area])
		if indebug:
		  print '13',ip,port,method,type,area.decode('utf8')
  return ret
		
			
#线程类

class TEST(threading.Thread):
    def __init__(self,action,index=None,checklist=None,checkmothed='http'):
        threading.Thread.__init__(self)
        self.index =index
        self.action=action
        self.checklist=checklist
        self.checkmothed=checkmothed

    def run(self):
        if (self.action=='getproxy'):
            get_proxy_one_website(self.index)
        else:
            check_proxy(self.index,self.checklist,self.checkmothed)


def check_proxy(index,checklist,checkmothed):
    for item in checklist:
        check_one_proxy(checkmothed,item[0],item[1],item[2])
        
def check_one_proxy(checkmothed,ip,port,method):
    global update_array
    global check_in_one_call
    global target_url,target_string,target_timeout
      
    url=target_url
    checkstr=target_string
    timeout=target_timeout
    if checkmothed=='http':
      if method==1:
        proxy_handler = urllib2.ProxyHandler({'http': 'http://'+ip+':'+str(port)+'/'})
        opener = urllib2.build_opener(proxy_handler)
        urllib2.install_opener(opener) 
      else:
        return  # socks4,socks5 退出函数处理     	  
      	  
    elif checkmothed=='connect':
      if method==1:
        socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, ip, int(port))
      elif method==2:
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS4, ip, int(port))
      elif method==3:
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, ip, int(port))
      socks.wrap_module(urllib2) 
         
    send_headers = {
          'User-agent':'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)'
          }
    t1=time.time()
    
    try:
    	req = urllib2.Request(url,headers=send_headers)
    	r  = urllib2.urlopen(req,timeout=20)	
    	rehtml=r.read()
    	pos=rehtml.find(checkstr)
    except Exception,e:
    	pos=-1
    	print e
    t2=time.time()	
    timeused=t2-t1
    if (timeused<timeout and pos>0):
       active=1
    else:
       active=0    
    update_array.append([ip,port,active,timeused]) 


def check_all_proxy(threadCount,checkmothed='http'):
    global check_in_one_call,skip_check_in_hour,cursor
    threads=[]        
    cursor.execute('select ip,port,method from proxy where active=0')
    rows = cursor.fetchall()  

    check_in_one_call=len(rows)
    
    #计算每个线程将要检查的代理个数
    if len(rows)>=threadCount:
        num_in_one_thread=len(rows)/threadCount   
    else:
        num_in_one_thread=1

    threadCount=threadCount+1
    print u"现在开始验证以下代理服务器....."
    for index in range(1,threadCount):        
     #分配每个线程要检查的checklist,并把那些剩余任务留给最后一个线程               
        checklist=rows[(index-1)*num_in_one_thread:index*num_in_one_thread]     
        if (index+1==threadCount):              
            checklist=rows[(index-1)*num_in_one_thread:]

        t=TEST('',index,checklist,checkmothed)
        t.setDaemon(True)
        t.start()
        threads.append((t))
    for thread in threads:
        thread.join(60)        
    update_proxies()            #把所有的检查结果更新到数据库
    

def get_proxy_one_website(index):
    global proxy_array
    func='build_list_urls_'+str(index)
    parse_func=eval('parse_page_'+str(index))
    urls=eval(func+'()')
    for url in urls:
        print url
        html=get_html(url)
        proxylist=parse_func(html)
        for proxy in proxylist:
            ip=string.strip(proxy[0])
            port=string.strip(proxy[1])
            if (re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$").search(ip)):
                method=str(proxy[2])
                type=str(proxy[3])
                area=string.strip(proxy[4])
                proxy_array.append([ip,port,method,type,area])


def get_all_proxies(webindex='0'):
    global web_site_count,cursor 
    threads=[]
    if webindex=='0':  
      print u"现在开始从以下"+str(web_site_count)+u"个网站抓取代理列表...."      
      count=web_site_count+1
      for index in range(1,count):
          t=TEST('getproxy',index)
          t.setDaemon(True)
          t.start()
          threads.append((t))
      for thread in threads:
          thread.join(60)
      add_proxies_to_db()
    else:
      print u"现在开始从以下第"+webindex+u"个网站抓取代理列表...."      
      t=TEST('getproxy',webindex)
      t.setDaemon(True)
      t.start()
      threads.append((t))
      for thread in threads:
          thread.join(60)             
    

def add_proxies_to_db():
    global proxy_array
    count=len(proxy_array)
    for i in range(count):
        item=proxy_array[i]
        cursor.execute("select ip from proxy where ip='"+item[0]+"'")
        iplist=cursor.fetchall()
        if len(iplist)==0:
          sql="""insert into `proxy` (`ip`,`port`,`method`,`type`,`intime`,`area`) values
          ('"""+item[0]+"',"+item[1]+","+item[2]+","+item[3]+",now(),'"+clean_string(item[4])+"')"        
          try:
            cursor.execute(sql)
          except Exception,e:
            print e


def update_proxies():
    global update_array
    for item in update_array:
        sql='''
             update `proxy` set `checktime`=now(), 
                `active`=%(active)01d, 
                 `speed`=%(speed)02.3f                 
                 where `ip`='%(ip)01s' and `port`=%(port)01d                            
            '''%{'active':item[2],'speed':item[3],'ip':item[0],'port':item[1]}
        try:
            cursor.execute(sql)    
        except:
            pass 

def clean_string(s):
    tmp=re.sub(r"['\,\s\\\/]", ' ', s)
    return re.sub(r"\s+", ' ', tmp)


def open_database():
    global conn,cursor,day_keep,db_host,db_port,db_user,db_passwd,db_database,db_charset,webindex    

    try:
      print db_host,db_port,db_user,db_passwd,db_database,db_charset    
      conn=MySQLdb.connect(host=db_host,port=db_port,user=db_user,passwd=db_passwd,db=db_database,charset=db_charset)
      cursor=conn.cursor()
    except:
      print u"连接数据库失败"
      sys.exit()  
    if webindex=='0':  #真正抓取网页的时候
      cursor.execute("delete from proxy where active=0 and checktime is not null")  #清理检测未通过的代理


def close_database():
    global cursor,conn
    cursor.close()
    conn.close()

if __name__ == '__main__':
    if len(sys.argv)<=1:
      usage()
      sys.exit()
    grab=False  #是否抓取网页
    check=False #是否检测代理
    try:
      opts, args = getopt.getopt(sys.argv[1:], "hgc:t:")
    except:
      usage()
      sys.exit()
    for op, value in opts:
      if op == "-h":
        usage()
        sys.exit()
      elif op== "-g":
       webindex='0'
       grab=True
      elif op=='-c':
       if value not in ['http','connect']:
         usage()
         sys.exit()
       webindex='0'
       check=True
       checkmethod=value
      elif op=="-t":
       webindex=value
       grab=True
      else:
        usage()
        sys.exit()      
    open_database()
    if grab==True:
      get_all_proxies(webindex)
    if check==True:
      check_all_proxy(thread_num,checkmethod)
    close_database()
    print u"所有工作已经完成"
