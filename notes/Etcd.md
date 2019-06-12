### Etcd 环境及操作


##### 授权
```shell
etcdctl --endpoints=${ENDPOINTS} --user=root role add ncfwxserv
etcdctl --endpoints=${ENDPOINTS} --user=root role grant-permission ncfwxserv readwrite /ncfwx/service	--prefix

etcdctl --endpoints=${ENDPOINTS} --user=root user add ncfwxserv
etcdctl --endpoints=${ENDPOINTS} --user=root user grant-role ncfwxserv ncfwxserv
```


```
root: vcnio4r902v
agwconfig: 9Cm9o34u2Al2VyGh
ncfwxserv: QmfgzQSkW7u48
```