checkproxy
=======

从网页抓取代理服务器，并验证代理是否可用

author: **hellstar**

> 需要安装python2.7环境

> 第三方python工具包 BeautifulSoup，MySQLdb

###用法

* 仅抓取代理

        proxy -g
   
* 仅验证代理

        proxy -c http            http - 验证HTTP代理，不验证socks4,socks5代理
        proxy -c connect         connect - 验证socks4,socks5代理和支持HTTP connect的HTTP代理
                
* 抓取代理并验证代理

        proxy -g -c http
    
* 测试抓取站点1

        proxy -t 1
    
* 查看帮助
    
        proxy -h


###配置参数

    web_site_count=13   #要抓取的网站数目
    indebug=1        
    
    thread_num=200                   # 开 thread_num 个线程检查代理
    check_in_one_call=thread_num*10  # 本次程序运行时 最多检查的代理个数
    
    db_host='localhost' # 数据库设置
    db_port=3306
    db_user='root'
    db_passwd='123456'
    db_database='social'
    db_charset='utf8'
    
    target_url="http://www.baidu.com/"   # 验证代理的时候通过代理访问这个地址
    target_string="030173"               # 如果返回的html中包含这个字符串，
    target_timeout=10                    # 并且响应时间小于 target_timeout 秒 
                                         # 那么我们就认为这个代理是有效的 
                                         
    proxy_use=1   #抓取时，是否使用代理
    proxy_ip='127.0.0.1'
    proxy_port='8087'

#已抓取的站点
*  [http://www.my-proxy.com](http://www.my-proxy.com)
*  [http://www.proxylists.net](http://www.proxylists.net)
*  [http://proxylist.sakura.ne.jp](http://proxylist.sakura.ne.jp)
*  [http://www.my-proxy.com](http://www.my-proxy.com)
*  [http://www.cybersyndrome.net](http://www.cybersyndrome.net)
*  [http://cn-proxy.com](http://cn-proxy.com)
*  [http://www.youdaili.cn](http://www.youdaili.cn)
*  [http://www.itmop.com](http://www.itmop.com)
*  [http://pachong.org](http://pachong.org)
*  [http://www.cz88.net](http://www.cz88.net)