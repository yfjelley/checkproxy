CREATE TABLE `proxy` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `ip` varchar(16) DEFAULT '' COMMENT 'ip地址',
  `port` int(11) DEFAULT '0' COMMENT '端口',
  `user` varchar(32) DEFAULT '' COMMENT 'SOCKE5用户名',
  `passwd` varchar(32) DEFAULT '' COMMENT 'SOCKE5密码',
  `type` int(11) DEFAULT '-1' COMMENT '代理类型 2:高匿 1:普匿 0:透明 -1: 未知',
  `method` int(11) DEFAULT '1' COMMENT '代理方式 1:HTTP 2:SOKS4 3:SOKS5',
  `active` int(11) DEFAULT '0' COMMENT '是否可用 0：不可用 1：可用',
  `area` varchar(128) DEFAULT '--' COMMENT '代理位置',
  `speed` float DEFAULT '0' COMMENT '速度',
  `intime` datetime DEFAULT NULL COMMENT '入库时间',
  `checktime` datetime DEFAULT NULL COMMENT '检查时间',
  PRIMARY KEY (`id`),
  KEY `Idx_method` (`method`),
  KEY `Idx_ip` (`ip`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8