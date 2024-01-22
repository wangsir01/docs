
遍历Windows操作系统的协议驱动

- - -

# 遍历Windows操作系统的协议驱动

## 前言

1.  搞Windows的，你应该写过协议驱动，你是否想过你写的协议驱动存放在哪里？可否遍历出？
2.  即使能在应用层的一些地方能看到协议驱动的一些信息，但是看不到协议驱动注册的函数。
3.  一些协议驱动偷偷的发送信息，一些早期的Windows版本上的WFP是拦截不到的（链路层）。

## IDA的简单分析

协议驱动的一个关键函数NdisRegisterProtocolDriver。  
IDA分析这个函数发现：

1.  申请个\_NDIS\_PROTOCOL\_BLOCK，
2.  调用ndisRegisterProtocolDriverCommon函数，把这个结构存储在ndisProtocolList链表里。
    
    ```plain
    Irql = KeAcquireSpinLockRaiseToDpc(&ndisProtocolListLock);
    ProtocolBlock->NextProtocol = ndisProtocolList; 
    ndisProtocolList = ProtocolBlock; 
    KeReleaseSpinLock(&ndisProtocolListLock, Irql);
    ```
    
3.  最后把这个结构的指针存储在（自己提供的）最后一个参数里。

所以得出枚举协议驱动的思路：

1.  自己安装个协议驱动，根据返回的句柄即\_NDIS\_PROTOCOL\_BLOCK \*，以及成员NextProtocol进行遍历。
2.  搜索定位全局但未导出的ndisProtocolList，类型是\_NDIS\_PROTOCOL\_BLOCK \*。注意锁：ndisProtocolListLock。
3.  看看有没有导出的API，有这个为最好。

## windbg手工操作

```plain
0: kd> x ndis!ndisProtocolList
fffff804`7cd9c6b8 ndis!ndisProtocolList = <no type information>
0: kd> dq poi(ndis!ndisProtocolList) L1
ffffe108`9a179010  00000000`038a0103
0: kd> dt poi(ndis!ndisProtocolList) _NDIS_PROTOCOL_BLOCK
ndis!_NDIS_PROTOCOL_BLOCK
   +0x000 Header           : _NDIS_OBJECT_HEADER
   +0x008 ProtocolDriverContext : 0xfffff804`8f988250 Void
   +0x010 NextProtocol     : 0xffffe108`9a1a5aa0 _NDIS_PROTOCOL_BLOCK
   +0x018 OpenQueue        : (null) 
   +0x020 Ref              : _REFERENCE_EX
   +0x038 MajorNdisVersion : 0x6 ''
   +0x039 MinorNdisVersion : 0x55 'U'
   +0x03a MajorDriverVersion : 0 ''
   +0x03b MinorDriverVersion : 0 ''
   +0x03c Reserved         : 0
   +0x040 Flags            : 0
   +0x048 Name             : _UNICODE_STRING "WANARPV6"
   +0x058 IsIPv4           : 0 ''
   +0x059 IsIPv6           : 0 ''
   +0x05a IsNdisTest6      : 0 ''
   +0x060 BindAdapterHandlerEx : 0xfffff804`8f9831f0     int  wanarp!WanNdisBindAdapter+0
   +0x068 UnbindAdapterHandlerEx : 0xfffff804`8f997530     int  wanarp!WanNdisUnbindAdapter+0
   +0x070 OpenAdapterCompleteHandlerEx : 0xfffff804`8f997390     void  wanarp!WanNdisOpenAdapterComplete+0
   +0x078 CloseAdapterCompleteHandlerEx : 0xfffff804`8f9972d0     void  wanarp!WanNdisCloseAdapterComplete+0
   +0x080 PnPEventHandler  : 0xfffff804`8f996ed0     int  wanarp!WanNdisPnPEvent+0
   +0x080 NetPnPEventHandler : 0xfffff804`8f996ed0     int  wanarp!WanNdisPnPEvent+0
   +0x088 UnloadHandler    : (null) 
   +0x090 UninstallHandler : (null) 
   +0x098 RequestCompleteHandler : (null) 
   +0x0a0 StatusHandlerEx  : 0xfffff804`8f981c80     void  wanarp!WanNdisStatus+0
   +0x0a0 StatusHandler    : 0xfffff804`8f981c80     void  wanarp!WanNdisStatus+0
   +0x0a8 StatusCompleteHandler : (null) 
   +0x0b0 ReceiveNetBufferListsHandler : 0xfffff804`8f981010     void  wanarp!WanNdisReceivePackets+0
   +0x0b8 SendNetBufferListsCompleteHandler : 0xfffff804`8f981780     void  wanarp!WanNdisSendComplete+0
   +0x0c0 CoStatusHandlerEx : (null) 
   +0x0c0 CoStatusHandler  : (null) 
   +0x0c8 CoAfRegisterNotifyHandler : (null) 
   +0x0d0 CoReceiveNetBufferListsHandler : (null) 
   +0x0d8 CoSendNetBufferListsCompleteHandler : (null) 
   +0x0e0 OpenAdapterCompleteHandler : (null) 
   +0x0e8 CloseAdapterCompleteHandler : (null) 
   +0x0f0 SendCompleteHandler : (null) 
   +0x0f0 WanSendCompleteHandler : (null) 
   +0x0f8 TransferDataCompleteHandler : (null) 
   +0x0f8 WanTransferDataCompleteHandler : (null) 
   +0x100 ResetCompleteHandler : (null) 
   +0x108 ReceiveHandler   : (null) 
   +0x108 WanReceiveHandler : (null) 
   +0x110 ReceiveCompleteHandler : (null) 
   +0x118 ReceivePacketHandler : (null) 
   +0x120 BindAdapterHandler : (null) 
   +0x128 UnbindAdapterHandler : (null) 
   +0x130 CoSendCompleteHandler : (null) 
   +0x138 CoReceivePacketHandler : (null) 
   +0x140 OidRequestCompleteHandler : 0xfffff804`8f983370     void  wanarp!WanNdisRequestComplete+0
   +0x148 WorkItem         : _WORK_QUEUE_ITEM
   +0x168 Mutex            : _KMUTANT
   +0x1a0 MutexOwnerThread : (null) 
   +0x1a8 MutexOwnerCount  : 0
   +0x1b0 BindDeviceName   : (null) 
   +0x1b8 RootDeviceName   : (null) 
   +0x1c0 AssociatedMiniDriver : (null) 
   +0x1c8 BindingAdapter   : (null) 
   +0x1d0 DeregEvent       : (null) 
   +0x1d8 ClientChars      : _NDIS_CO_CLIENT_OPTIONAL_HANDLERS
   +0x278 CallMgrChars     : _NDIS_CO_CALL_MANAGER_OPTIONAL_HANDLERS
   +0x308 DirectOidRequestCompleteHandler : (null) 
   +0x310 AllocateSharedMemoryHandler : (null) 
   +0x318 FreeSharedMemoryHandler : (null) 
   +0x320 AllocateSharedMemoryContext : (null) 
   +0x328 ImageName        : _UNICODE_STRING "wanarp.sys"
   +0x338 Bind             : KRef<NDIS_BIND_PROTOCOL_DRIVER>
   +0x340 NotifyBindCompleteWorkItem : KCoalescingWorkItem<_NDIS_PROTOCOL_BLOCK>
0: kd> dt 0xffffe108`9a1a5aa0 _NDIS_PROTOCOL_BLOCK
ndis!_NDIS_PROTOCOL_BLOCK
   +0x000 Header           : _NDIS_OBJECT_HEADER
   +0x008 ProtocolDriverContext : 0xfffff804`8f988000 Void
   +0x010 NextProtocol     : 0xffffe108`9de60ae0 _NDIS_PROTOCOL_BLOCK
   +0x018 OpenQueue        : (null) 
   +0x020 Ref              : _REFERENCE_EX
   +0x038 MajorNdisVersion : 0x6 ''
   +0x039 MinorNdisVersion : 0x55 'U'
   +0x03a MajorDriverVersion : 0 ''
   +0x03b MinorDriverVersion : 0 ''
   +0x03c Reserved         : 0
   +0x040 Flags            : 0
   +0x048 Name             : _UNICODE_STRING "WANARP"
   +0x058 IsIPv4           : 0 ''
   +0x059 IsIPv6           : 0 ''
   +0x05a IsNdisTest6      : 0 ''
   +0x060 BindAdapterHandlerEx : 0xfffff804`8f9831f0     int  wanarp!WanNdisBindAdapter+0
   +0x068 UnbindAdapterHandlerEx : 0xfffff804`8f997530     int  wanarp!WanNdisUnbindAdapter+0
   +0x070 OpenAdapterCompleteHandlerEx : 0xfffff804`8f997390     void  wanarp!WanNdisOpenAdapterComplete+0
   +0x078 CloseAdapterCompleteHandlerEx : 0xfffff804`8f9972d0     void  wanarp!WanNdisCloseAdapterComplete+0
   +0x080 PnPEventHandler  : 0xfffff804`8f996ed0     int  wanarp!WanNdisPnPEvent+0
   +0x080 NetPnPEventHandler : 0xfffff804`8f996ed0     int  wanarp!WanNdisPnPEvent+0
   +0x088 UnloadHandler    : (null) 
   +0x090 UninstallHandler : (null) 
   +0x098 RequestCompleteHandler : (null) 
   +0x0a0 StatusHandlerEx  : 0xfffff804`8f981c80     void  wanarp!WanNdisStatus+0
   +0x0a0 StatusHandler    : 0xfffff804`8f981c80     void  wanarp!WanNdisStatus+0
   +0x0a8 StatusCompleteHandler : (null) 
   +0x0b0 ReceiveNetBufferListsHandler : 0xfffff804`8f981010     void  wanarp!WanNdisReceivePackets+0
   +0x0b8 SendNetBufferListsCompleteHandler : 0xfffff804`8f981780     void  wanarp!WanNdisSendComplete+0
   +0x0c0 CoStatusHandlerEx : (null) 
   +0x0c0 CoStatusHandler  : (null) 
   +0x0c8 CoAfRegisterNotifyHandler : (null) 
   +0x0d0 CoReceiveNetBufferListsHandler : (null) 
   +0x0d8 CoSendNetBufferListsCompleteHandler : (null) 
   +0x0e0 OpenAdapterCompleteHandler : (null) 
   +0x0e8 CloseAdapterCompleteHandler : (null) 
   +0x0f0 SendCompleteHandler : (null) 
   +0x0f0 WanSendCompleteHandler : (null) 
   +0x0f8 TransferDataCompleteHandler : (null) 
   +0x0f8 WanTransferDataCompleteHandler : (null) 
   +0x100 ResetCompleteHandler : (null) 
   +0x108 ReceiveHandler   : (null) 
   +0x108 WanReceiveHandler : (null) 
   +0x110 ReceiveCompleteHandler : (null) 
   +0x118 ReceivePacketHandler : (null) 
   +0x120 BindAdapterHandler : (null) 
   +0x128 UnbindAdapterHandler : (null) 
   +0x130 CoSendCompleteHandler : (null) 
   +0x138 CoReceivePacketHandler : (null) 
   +0x140 OidRequestCompleteHandler : 0xfffff804`8f983370     void  wanarp!WanNdisRequestComplete+0
   +0x148 WorkItem         : _WORK_QUEUE_ITEM
   +0x168 Mutex            : _KMUTANT
   +0x1a0 MutexOwnerThread : (null) 
   +0x1a8 MutexOwnerCount  : 0
   +0x1b0 BindDeviceName   : (null) 
   +0x1b8 RootDeviceName   : (null) 
   +0x1c0 AssociatedMiniDriver : (null) 
   +0x1c8 BindingAdapter   : (null) 
   +0x1d0 DeregEvent       : (null) 
   +0x1d8 ClientChars      : _NDIS_CO_CLIENT_OPTIONAL_HANDLERS
   +0x278 CallMgrChars     : _NDIS_CO_CALL_MANAGER_OPTIONAL_HANDLERS
   +0x308 DirectOidRequestCompleteHandler : (null) 
   +0x310 AllocateSharedMemoryHandler : (null) 
   +0x318 FreeSharedMemoryHandler : (null) 
   +0x320 AllocateSharedMemoryContext : (null) 
   +0x328 ImageName        : _UNICODE_STRING "wanarp.sys"
   +0x338 Bind             : KRef<NDIS_BIND_PROTOCOL_DRIVER>
   +0x340 NotifyBindCompleteWorkItem : KCoalescingWorkItem<_NDIS_PROTOCOL_BLOCK>
0: kd> dt 0xffffe108`9de60ae0 _NDIS_PROTOCOL_BLOCK
ndis!_NDIS_PROTOCOL_BLOCK
   +0x000 Header           : _NDIS_OBJECT_HEADER
   +0x008 ProtocolDriverContext : (null) 
   +0x010 NextProtocol     : 0xffffe108`9a16eb30 _NDIS_PROTOCOL_BLOCK
   +0x018 OpenQueue        : 0xffffe108`9dde9aa0 _NDIS_OPEN_BLOCK
   +0x020 Ref              : _REFERENCE_EX
   +0x038 MajorNdisVersion : 0x6 ''
   +0x039 MinorNdisVersion : 0x1e ''
   +0x03a MajorDriverVersion : 0 ''
   +0x03b MinorDriverVersion : 0 ''
   +0x03c Reserved         : 0
   +0x040 Flags            : 0
   +0x048 Name             : _UNICODE_STRING "RSPNDR"
   +0x058 IsIPv4           : 0 ''
   +0x059 IsIPv6           : 0 ''
   +0x05a IsNdisTest6      : 0 ''
   +0x060 BindAdapterHandlerEx : 0xfffff804`8f961260     int  rspndr!ToppBindAdapterHandlerEx+0
   +0x068 UnbindAdapterHandlerEx : 0xfffff804`8f964a40     int  rspndr!ToppUnbindAdapterHandlerEx+0
   +0x070 OpenAdapterCompleteHandlerEx : 0xfffff804`8f9644a0     void  rspndr!ToppOpenAdapterCompleteHandlerEx+0
   +0x078 CloseAdapterCompleteHandlerEx : 0xfffff804`8f964460     void  rspndr!ToppCloseAdapterCompleteHandlerEx+0
   +0x080 PnPEventHandler  : 0xfffff804`8f962040     int  rspndr!ToppPnPEventHandler+0
   +0x080 NetPnPEventHandler : 0xfffff804`8f962040     int  rspndr!ToppPnPEventHandler+0
   +0x088 UnloadHandler    : (null) 
   +0x090 UninstallHandler : (null) 
   +0x098 RequestCompleteHandler : (null) 
   +0x0a0 StatusHandlerEx  : 0xfffff804`8f961010     void  rspndr!ToppStatusHandlerEx+0
   +0x0a0 StatusHandler    : 0xfffff804`8f961010     void  rspndr!ToppStatusHandlerEx+0
   +0x0a8 StatusCompleteHandler : (null) 
   +0x0b0 ReceiveNetBufferListsHandler : 0xfffff804`8f9644d0     void  rspndr!ToppReceiveNetBufferListHandler+0
   +0x0b8 SendNetBufferListsCompleteHandler : 0xfffff804`8f9649c0     void  rspndr!ToppSendNetBufferListsCompleteHandler+0
   +0x0c0 CoStatusHandlerEx : (null) 
   +0x0c0 CoStatusHandler  : (null) 
   +0x0c8 CoAfRegisterNotifyHandler : (null) 
   +0x0d0 CoReceiveNetBufferListsHandler : (null) 
   +0x0d8 CoSendNetBufferListsCompleteHandler : (null) 
   +0x0e0 OpenAdapterCompleteHandler : (null) 
   +0x0e8 CloseAdapterCompleteHandler : (null) 
   +0x0f0 SendCompleteHandler : (null) 
   +0x0f0 WanSendCompleteHandler : (null) 
   +0x0f8 TransferDataCompleteHandler : (null) 
   +0x0f8 WanTransferDataCompleteHandler : (null) 
   +0x100 ResetCompleteHandler : (null) 
   +0x108 ReceiveHandler   : (null) 
   +0x108 WanReceiveHandler : (null) 
   +0x110 ReceiveCompleteHandler : (null) 
   +0x118 ReceivePacketHandler : (null) 
   +0x120 BindAdapterHandler : (null) 
   +0x128 UnbindAdapterHandler : (null) 
   +0x130 CoSendCompleteHandler : (null) 
   +0x138 CoReceivePacketHandler : (null) 
   +0x140 OidRequestCompleteHandler : 0xfffff804`8f962140     void  rspndr!ToppOidRequestCompleteHandler+0
   +0x148 WorkItem         : _WORK_QUEUE_ITEM
   +0x168 Mutex            : _KMUTANT
   +0x1a0 MutexOwnerThread : (null) 
   +0x1a8 MutexOwnerCount  : 0
   +0x1b0 BindDeviceName   : (null) 
   +0x1b8 RootDeviceName   : 0xffffe108`9a8bf2b8 _UNICODE_STRING "\DEVICE\{65174C02-ADC6-4292-B214-E79177770A8E}"
   +0x1c0 AssociatedMiniDriver : (null) 
   +0x1c8 BindingAdapter   : 0xffffe108`9c5e81a0 _NDIS_MINIPORT_BLOCK
   +0x1d0 DeregEvent       : (null) 
   +0x1d8 ClientChars      : _NDIS_CO_CLIENT_OPTIONAL_HANDLERS
   +0x278 CallMgrChars     : _NDIS_CO_CALL_MANAGER_OPTIONAL_HANDLERS
   +0x308 DirectOidRequestCompleteHandler : (null) 
   +0x310 AllocateSharedMemoryHandler : (null) 
   +0x318 FreeSharedMemoryHandler : (null) 
   +0x320 AllocateSharedMemoryContext : (null) 
   +0x328 ImageName        : _UNICODE_STRING "rspndr.sys"
   +0x338 Bind             : KRef<NDIS_BIND_PROTOCOL_DRIVER>
   +0x340 NotifyBindCompleteWorkItem : KCoalescingWorkItem<_NDIS_PROTOCOL_BLOCK>
0: kd> dt 0xffffe108`9a16eb30 _NDIS_PROTOCOL_BLOCK
ndis!_NDIS_PROTOCOL_BLOCK
   +0x000 Header           : _NDIS_OBJECT_HEADER
   +0x008 ProtocolDriverContext : 0xfffff804`8f949220 Void
   +0x010 NextProtocol     : 0xffffe108`9a16cb30 _NDIS_PROTOCOL_BLOCK
   +0x018 OpenQueue        : 0xffffe108`9ddeaaa0 _NDIS_OPEN_BLOCK
   +0x020 Ref              : _REFERENCE_EX
   +0x038 MajorNdisVersion : 0x6 ''
   +0x039 MinorNdisVersion : 0x1e ''
   +0x03a MajorDriverVersion : 0xa ''
   +0x03b MinorDriverVersion : 0 ''
   +0x03c Reserved         : 0
   +0x040 Flags            : 0
   +0x048 Name             : _UNICODE_STRING "MSLLDP"
   +0x058 IsIPv4           : 0 ''
   +0x059 IsIPv6           : 0 ''
   +0x05a IsNdisTest6      : 0 ''
   +0x060 BindAdapterHandlerEx : 0xfffff804`8f94ca70     int  mslldp!lldpProtBindAdapter+0
   +0x068 UnbindAdapterHandlerEx : 0xfffff804`8f94d170     int  mslldp!lldpProtUnbindAdapter+0
   +0x070 OpenAdapterCompleteHandlerEx : 0xfffff804`8f94cf80     void  mslldp!lldpProtOpenAdapterComplete+0
   +0x078 CloseAdapterCompleteHandlerEx : 0xfffff804`8f94cc20     void  mslldp!lldpProtCloseAdapterComplete+0
   +0x080 PnPEventHandler  : 0xfffff804`8f94cc40     int  mslldp!lldpProtNetPnPEvent+0
   +0x080 NetPnPEventHandler : 0xfffff804`8f94cc40     int  mslldp!lldpProtNetPnPEvent+0
   +0x088 UnloadHandler    : (null) 
   +0x090 UninstallHandler : (null) 
   +0x098 RequestCompleteHandler : (null) 
   +0x0a0 StatusHandlerEx  : 0xfffff804`8f942a90     void  mslldp!lldpProtStatus+0
   +0x0a0 StatusHandler    : 0xfffff804`8f942a90     void  mslldp!lldpProtStatus+0
   +0x0a8 StatusCompleteHandler : (null) 
   +0x0b0 ReceiveNetBufferListsHandler : 0xfffff804`8f941010     void  mslldp!lldpProtReceiveNetBufferLists+0
   +0x0b8 SendNetBufferListsCompleteHandler : 0xfffff804`8f942a50     void  mslldp!lldpProtSendNetBufferListsComplete+0
   +0x0c0 CoStatusHandlerEx : (null) 
   +0x0c0 CoStatusHandler  : (null) 
   +0x0c8 CoAfRegisterNotifyHandler : (null) 
   +0x0d0 CoReceiveNetBufferListsHandler : (null) 
   +0x0d8 CoSendNetBufferListsCompleteHandler : (null) 
   +0x0e0 OpenAdapterCompleteHandler : (null) 
   +0x0e8 CloseAdapterCompleteHandler : (null) 
   +0x0f0 SendCompleteHandler : (null) 
   +0x0f0 WanSendCompleteHandler : (null) 
   +0x0f8 TransferDataCompleteHandler : (null) 
   +0x0f8 WanTransferDataCompleteHandler : (null) 
   +0x100 ResetCompleteHandler : (null) 
   +0x108 ReceiveHandler   : (null) 
   +0x108 WanReceiveHandler : (null) 
   +0x110 ReceiveCompleteHandler : (null) 
   +0x118 ReceivePacketHandler : (null) 
   +0x120 BindAdapterHandler : (null) 
   +0x128 UnbindAdapterHandler : (null) 
   +0x130 CoSendCompleteHandler : (null) 
   +0x138 CoReceivePacketHandler : (null) 
   +0x140 OidRequestCompleteHandler : 0xfffff804`8f942a20     void  mslldp!lldpProtOidRequestComplete+0
   +0x148 WorkItem         : _WORK_QUEUE_ITEM
   +0x168 Mutex            : _KMUTANT
   +0x1a0 MutexOwnerThread : (null) 
   +0x1a8 MutexOwnerCount  : 0
   +0x1b0 BindDeviceName   : (null) 
   +0x1b8 RootDeviceName   : 0xffffe108`9a8bf2b8 _UNICODE_STRING "\DEVICE\{65174C02-ADC6-4292-B214-E79177770A8E}"
   +0x1c0 AssociatedMiniDriver : (null) 
   +0x1c8 BindingAdapter   : 0xffffe108`9c5e81a0 _NDIS_MINIPORT_BLOCK
   +0x1d0 DeregEvent       : (null) 
   +0x1d8 ClientChars      : _NDIS_CO_CLIENT_OPTIONAL_HANDLERS
   +0x278 CallMgrChars     : _NDIS_CO_CALL_MANAGER_OPTIONAL_HANDLERS
   +0x308 DirectOidRequestCompleteHandler : (null) 
   +0x310 AllocateSharedMemoryHandler : (null) 
   +0x318 FreeSharedMemoryHandler : (null) 
   +0x320 AllocateSharedMemoryContext : (null) 
   +0x328 ImageName        : _UNICODE_STRING "mslldp.sys"
   +0x338 Bind             : KRef<NDIS_BIND_PROTOCOL_DRIVER>
   +0x340 NotifyBindCompleteWorkItem : KCoalescingWorkItem<_NDIS_PROTOCOL_BLOCK>
0: kd> dt 0xffffe108`9a16cb30 _NDIS_PROTOCOL_BLOCK
ndis!_NDIS_PROTOCOL_BLOCK
   +0x000 Header           : _NDIS_OBJECT_HEADER
   +0x008 ProtocolDriverContext : (null) 
   +0x010 NextProtocol     : 0xffffe108`9c4998a0 _NDIS_PROTOCOL_BLOCK
   +0x018 OpenQueue        : 0xffffe108`9ddebaa0 _NDIS_OPEN_BLOCK
   +0x020 Ref              : _REFERENCE_EX
   +0x038 MajorNdisVersion : 0x6 ''
   +0x039 MinorNdisVersion : 0x1e ''
   +0x03a MajorDriverVersion : 0 ''
   +0x03b MinorDriverVersion : 0 ''
   +0x03c Reserved         : 0
   +0x040 Flags            : 0
   +0x048 Name             : _UNICODE_STRING "LLTDIO"
   +0x058 IsIPv4           : 0 ''
   +0x059 IsIPv6           : 0 ''
   +0x05a IsNdisTest6      : 0 ''
   +0x060 BindAdapterHandlerEx : 0xfffff804`8f9214d0     int  lltdio!ToppBindAdapterHandlerEx+0
   +0x068 UnbindAdapterHandlerEx : 0xfffff804`8f923c90     int  lltdio!ToppUnbindAdapterHandlerEx+0
   +0x070 OpenAdapterCompleteHandlerEx : 0xfffff804`8f9236d0     void  lltdio!ToppOpenAdapterCompleteHandlerEx+0
   +0x078 CloseAdapterCompleteHandlerEx : 0xfffff804`8f923680     void  lltdio!ToppCloseAdapterCompleteHandlerEx+0
   +0x080 PnPEventHandler  : 0xfffff804`8f921c20     int  lltdio!ToppPnPEventHandler+0
   +0x080 NetPnPEventHandler : 0xfffff804`8f921c20     int  lltdio!ToppPnPEventHandler+0
   +0x088 UnloadHandler    : (null) 
   +0x090 UninstallHandler : (null) 
   +0x098 RequestCompleteHandler : (null) 
   +0x0a0 StatusHandlerEx  : 0xfffff804`8f921e00     void  lltdio!ToppStatusHandlerEx+0
   +0x0a0 StatusHandler    : 0xfffff804`8f921e00     void  lltdio!ToppStatusHandlerEx+0
   +0x0a8 StatusCompleteHandler : (null) 
   +0x0b0 ReceiveNetBufferListsHandler : 0xfffff804`8f923700     void  lltdio!ToppReceiveNetBufferListHandler+0
   +0x0b8 SendNetBufferListsCompleteHandler : 0xfffff804`8f923bd0     void  lltdio!ToppSendNetBufferListsCompleteHandler+0
   +0x0c0 CoStatusHandlerEx : (null) 
   +0x0c0 CoStatusHandler  : (null) 
   +0x0c8 CoAfRegisterNotifyHandler : (null) 
   +0x0d0 CoReceiveNetBufferListsHandler : (null) 
   +0x0d8 CoSendNetBufferListsCompleteHandler : (null) 
   +0x0e0 OpenAdapterCompleteHandler : (null) 
   +0x0e8 CloseAdapterCompleteHandler : (null) 
   +0x0f0 SendCompleteHandler : (null) 
   +0x0f0 WanSendCompleteHandler : (null) 
   +0x0f8 TransferDataCompleteHandler : (null) 
   +0x0f8 WanTransferDataCompleteHandler : (null) 
   +0x100 ResetCompleteHandler : (null) 
   +0x108 ReceiveHandler   : (null) 
   +0x108 WanReceiveHandler : (null) 
   +0x110 ReceiveCompleteHandler : (null) 
   +0x118 ReceivePacketHandler : (null) 
   +0x120 BindAdapterHandler : (null) 
   +0x128 UnbindAdapterHandler : (null) 
   +0x130 CoSendCompleteHandler : (null) 
   +0x138 CoReceivePacketHandler : (null) 
   +0x140 OidRequestCompleteHandler : 0xfffff804`8f921e90     void  lltdio!TopOidRequestCompleteHandler+0
   +0x148 WorkItem         : _WORK_QUEUE_ITEM
   +0x168 Mutex            : _KMUTANT
   +0x1a0 MutexOwnerThread : (null) 
   +0x1a8 MutexOwnerCount  : 0
   +0x1b0 BindDeviceName   : (null) 
   +0x1b8 RootDeviceName   : 0xffffe108`9a80e9c8 _UNICODE_STRING "\DEVICE\{369292E4-DD92-46B9-B680-A71531F1B46E}"
   +0x1c0 AssociatedMiniDriver : (null) 
   +0x1c8 BindingAdapter   : 0xffffe108`9dacf1a0 _NDIS_MINIPORT_BLOCK
   +0x1d0 DeregEvent       : (null) 
   +0x1d8 ClientChars      : _NDIS_CO_CLIENT_OPTIONAL_HANDLERS
   +0x278 CallMgrChars     : _NDIS_CO_CALL_MANAGER_OPTIONAL_HANDLERS
   +0x308 DirectOidRequestCompleteHandler : (null) 
   +0x310 AllocateSharedMemoryHandler : (null) 
   +0x318 FreeSharedMemoryHandler : (null) 
   +0x320 AllocateSharedMemoryContext : (null) 
   +0x328 ImageName        : _UNICODE_STRING "lltdio.sys"
   +0x338 Bind             : KRef<NDIS_BIND_PROTOCOL_DRIVER>
   +0x340 NotifyBindCompleteWorkItem : KCoalescingWorkItem<_NDIS_PROTOCOL_BLOCK>
0: kd> dt 0xffffe108`9c4998a0 _NDIS_PROTOCOL_BLOCK
ndis!_NDIS_PROTOCOL_BLOCK
   +0x000 Header           : _NDIS_OBJECT_HEADER
   +0x008 ProtocolDriverContext : 0xfffff804`7d12cfb0 Void
   +0x010 NextProtocol     : 0xffffe108`9c27c8a0 _NDIS_PROTOCOL_BLOCK
   +0x018 OpenQueue        : (null) 
   +0x020 Ref              : _REFERENCE_EX
   +0x038 MajorNdisVersion : 0x6 ''
   +0x039 MinorNdisVersion : 0x28 '('
   +0x03a MajorDriverVersion : 0 ''
   +0x03b MinorDriverVersion : 0 ''
   +0x03c Reserved         : 0
   +0x040 Flags            : 0
   +0x048 Name             : _UNICODE_STRING "RDMANDK"
   +0x058 IsIPv4           : 0 ''
   +0x059 IsIPv6           : 0 ''
   +0x05a IsNdisTest6      : 0 ''
   +0x060 BindAdapterHandlerEx : 0xfffff804`7cfc7f80     int  tcpip!FlRdmaBindAdapter+0
   +0x068 UnbindAdapterHandlerEx : 0xfffff804`7d0db690     int  tcpip!FlRdmaUnbindAdapter+0
   +0x070 OpenAdapterCompleteHandlerEx : 0xfffff804`7d0d1d30     void  tcpip!FlOpenAdapterComplete+0
   +0x078 CloseAdapterCompleteHandlerEx : 0xfffff804`7cfb0420     void  tcpip!FlCloseAdapterComplete+0
   +0x080 PnPEventHandler  : 0xfffff804`7cfc7a60     int  tcpip!FlRdmaPnpEvent+0
   +0x080 NetPnPEventHandler : 0xfffff804`7cfc7a60     int  tcpip!FlRdmaPnpEvent+0
   +0x088 UnloadHandler    : (null) 
   +0x090 UninstallHandler : (null) 
   +0x098 RequestCompleteHandler : (null) 
   +0x0a0 StatusHandlerEx  : 0xfffff804`7cfab520     void  tcpip!Fl4lCleanup+0
   +0x0a0 StatusHandler    : 0xfffff804`7cfab520     void  tcpip!Fl4lCleanup+0
   +0x0a8 StatusCompleteHandler : (null) 
   +0x0b0 ReceiveNetBufferListsHandler : 0xfffff804`7cfab520     void  tcpip!Fl4lCleanup+0
   +0x0b8 SendNetBufferListsCompleteHandler : 0xfffff804`7cfab520     void  tcpip!Fl4lCleanup+0
   +0x0c0 CoStatusHandlerEx : (null) 
   +0x0c0 CoStatusHandler  : (null) 
   +0x0c8 CoAfRegisterNotifyHandler : (null) 
   +0x0d0 CoReceiveNetBufferListsHandler : (null) 
   +0x0d8 CoSendNetBufferListsCompleteHandler : (null) 
   +0x0e0 OpenAdapterCompleteHandler : (null) 
   +0x0e8 CloseAdapterCompleteHandler : (null) 
   +0x0f0 SendCompleteHandler : (null) 
   +0x0f0 WanSendCompleteHandler : (null) 
   +0x0f8 TransferDataCompleteHandler : (null) 
   +0x0f8 WanTransferDataCompleteHandler : (null) 
   +0x100 ResetCompleteHandler : (null) 
   +0x108 ReceiveHandler   : (null) 
   +0x108 WanReceiveHandler : (null) 
   +0x110 ReceiveCompleteHandler : (null) 
   +0x118 ReceivePacketHandler : (null) 
   +0x120 BindAdapterHandler : (null) 
   +0x128 UnbindAdapterHandler : (null) 
   +0x130 CoSendCompleteHandler : (null) 
   +0x138 CoReceivePacketHandler : (null) 
   +0x140 OidRequestCompleteHandler : 0xfffff804`7cfa6dc0     void  tcpip!FlDirectRequestComplete+0
   +0x148 WorkItem         : _WORK_QUEUE_ITEM
   +0x168 Mutex            : _KMUTANT
   +0x1a0 MutexOwnerThread : (null) 
   +0x1a8 MutexOwnerCount  : 0
   +0x1b0 BindDeviceName   : 0xffffe108`9dad0080 _UNICODE_STRING "\DEVICE\{369292E4-DD92-46B9-B680-A71531F1B46E}"
   +0x1b8 RootDeviceName   : 0xffffe108`9a80e9c8 _UNICODE_STRING "\DEVICE\{369292E4-DD92-46B9-B680-A71531F1B46E}"
   +0x1c0 AssociatedMiniDriver : (null) 
   +0x1c8 BindingAdapter   : 0xffffe108`9dacf1a0 _NDIS_MINIPORT_BLOCK
   +0x1d0 DeregEvent       : (null) 
   +0x1d8 ClientChars      : _NDIS_CO_CLIENT_OPTIONAL_HANDLERS
   +0x278 CallMgrChars     : _NDIS_CO_CALL_MANAGER_OPTIONAL_HANDLERS
   +0x308 DirectOidRequestCompleteHandler : 0xfffff804`7cfa6dc0     void  tcpip!FlDirectRequestComplete+0
   +0x310 AllocateSharedMemoryHandler : (null) 
   +0x318 FreeSharedMemoryHandler : (null) 
   +0x320 AllocateSharedMemoryContext : (null) 
   +0x328 ImageName        : _UNICODE_STRING ""
   +0x338 Bind             : KRef<NDIS_BIND_PROTOCOL_DRIVER>
   +0x340 NotifyBindCompleteWorkItem : KCoalescingWorkItem<_NDIS_PROTOCOL_BLOCK>
0: kd> dt 0xffffe108`9c27c8a0 _NDIS_PROTOCOL_BLOCK
ndis!_NDIS_PROTOCOL_BLOCK
   +0x000 Header           : _NDIS_OBJECT_HEADER
   +0x008 ProtocolDriverContext : 0xfffff804`7d132ec0 Void
   +0x010 NextProtocol     : 0xffffe108`9c297430 _NDIS_PROTOCOL_BLOCK
   +0x018 OpenQueue        : (null) 
   +0x020 Ref              : _REFERENCE_EX
   +0x038 MajorNdisVersion : 0x6 ''
   +0x039 MinorNdisVersion : 0x28 '('
   +0x03a MajorDriverVersion : 0 ''
   +0x03b MinorDriverVersion : 0 ''
   +0x03c Reserved         : 0
   +0x040 Flags            : 0
   +0x048 Name             : _UNICODE_STRING "TCPIP6TUNNEL"
   +0x058 IsIPv4           : 0 ''
   +0x059 IsIPv6           : 0 ''
   +0x05a IsNdisTest6      : 0 ''
   +0x060 BindAdapterHandlerEx : 0xfffff804`7cfbff70     int  tcpip!FlBindAdapter+0
   +0x068 UnbindAdapterHandlerEx : 0xfffff804`7cfae5d0     int  tcpip!FlUnbindAdapter+0
   +0x070 OpenAdapterCompleteHandlerEx : 0xfffff804`7d0d1d30     void  tcpip!FlOpenAdapterComplete+0
   +0x078 CloseAdapterCompleteHandlerEx : 0xfffff804`7cfb0420     void  tcpip!FlCloseAdapterComplete+0
   +0x080 PnPEventHandler  : 0xfffff804`7cfe2e60     int  tcpip!Fl6tPnpEvent+0
   +0x080 NetPnPEventHandler : 0xfffff804`7cfe2e60     int  tcpip!Fl6tPnpEvent+0
   +0x088 UnloadHandler    : (null) 
   +0x090 UninstallHandler : (null) 
   +0x098 RequestCompleteHandler : (null) 
   +0x0a0 StatusHandlerEx  : 0xfffff804`7cfc1fe0     void  tcpip!FlStatus+0
   +0x0a0 StatusHandler    : 0xfffff804`7cfc1fe0     void  tcpip!FlStatus+0
   +0x0a8 StatusCompleteHandler : (null) 
   +0x0b0 ReceiveNetBufferListsHandler : 0xfffff804`7cf96d80     void  tcpip!FlReceiveNetBufferListChain+0
   +0x0b8 SendNetBufferListsCompleteHandler : 0xfffff804`7cf986d0     void  tcpip!FlSendNetBufferListChainComplete+0
   +0x0c0 CoStatusHandlerEx : (null) 
   +0x0c0 CoStatusHandler  : (null) 
   +0x0c8 CoAfRegisterNotifyHandler : (null) 
   +0x0d0 CoReceiveNetBufferListsHandler : (null) 
   +0x0d8 CoSendNetBufferListsCompleteHandler : (null) 
   +0x0e0 OpenAdapterCompleteHandler : (null) 
   +0x0e8 CloseAdapterCompleteHandler : (null) 
   +0x0f0 SendCompleteHandler : (null) 
   +0x0f0 WanSendCompleteHandler : (null) 
   +0x0f8 TransferDataCompleteHandler : (null) 
   +0x0f8 WanTransferDataCompleteHandler : (null) 
   +0x100 ResetCompleteHandler : (null) 
   +0x108 ReceiveHandler   : (null) 
   +0x108 WanReceiveHandler : (null) 
   +0x110 ReceiveCompleteHandler : (null) 
   +0x118 ReceivePacketHandler : (null) 
   +0x120 BindAdapterHandler : (null) 
   +0x128 UnbindAdapterHandler : (null) 
   +0x130 CoSendCompleteHandler : (null) 
   +0x138 CoReceivePacketHandler : (null) 
   +0x140 OidRequestCompleteHandler : 0xfffff804`7cfa6dc0     void  tcpip!FlDirectRequestComplete+0
   +0x148 WorkItem         : _WORK_QUEUE_ITEM
   +0x168 Mutex            : _KMUTANT
   +0x1a0 MutexOwnerThread : (null) 
   +0x1a8 MutexOwnerCount  : 0
   +0x1b0 BindDeviceName   : (null) 
   +0x1b8 RootDeviceName   : (null) 
   +0x1c0 AssociatedMiniDriver : (null) 
   +0x1c8 BindingAdapter   : (null) 
   +0x1d0 DeregEvent       : (null) 
   +0x1d8 ClientChars      : _NDIS_CO_CLIENT_OPTIONAL_HANDLERS
   +0x278 CallMgrChars     : _NDIS_CO_CALL_MANAGER_OPTIONAL_HANDLERS
   +0x308 DirectOidRequestCompleteHandler : 0xfffff804`7cfa6dc0     void  tcpip!FlDirectRequestComplete+0
   +0x310 AllocateSharedMemoryHandler : (null) 
   +0x318 FreeSharedMemoryHandler : (null) 
   +0x320 AllocateSharedMemoryContext : (null) 
   +0x328 ImageName        : _UNICODE_STRING ""
   +0x338 Bind             : KRef<NDIS_BIND_PROTOCOL_DRIVER>
   +0x340 NotifyBindCompleteWorkItem : KCoalescingWorkItem<_NDIS_PROTOCOL_BLOCK>
0: kd> dt 0xffffe108`9c297430 _NDIS_PROTOCOL_BLOCK
ndis!_NDIS_PROTOCOL_BLOCK
   +0x000 Header           : _NDIS_OBJECT_HEADER
   +0x008 ProtocolDriverContext : 0xfffff804`7d132c20 Void
   +0x010 NextProtocol     : 0xffffe108`9c26bb30 _NDIS_PROTOCOL_BLOCK
   +0x018 OpenQueue        : (null) 
   +0x020 Ref              : _REFERENCE_EX
   +0x038 MajorNdisVersion : 0x6 ''
   +0x039 MinorNdisVersion : 0x28 '('
   +0x03a MajorDriverVersion : 0 ''
   +0x03b MinorDriverVersion : 0 ''
   +0x03c Reserved         : 0
   +0x040 Flags            : 0
   +0x048 Name             : _UNICODE_STRING "TCPIPTUNNEL"
   +0x058 IsIPv4           : 0 ''
   +0x059 IsIPv6           : 0 ''
   +0x05a IsNdisTest6      : 0 ''
   +0x060 BindAdapterHandlerEx : 0xfffff804`7cfbff70     int  tcpip!FlBindAdapter+0
   +0x068 UnbindAdapterHandlerEx : 0xfffff804`7cfae5d0     int  tcpip!FlUnbindAdapter+0
   +0x070 OpenAdapterCompleteHandlerEx : 0xfffff804`7d0d1d30     void  tcpip!FlOpenAdapterComplete+0
   +0x078 CloseAdapterCompleteHandlerEx : 0xfffff804`7cfb0420     void  tcpip!FlCloseAdapterComplete+0
   +0x080 PnPEventHandler  : 0xfffff804`7cfe2e90     int  tcpip!Fl4tPnpEvent+0
   +0x080 NetPnPEventHandler : 0xfffff804`7cfe2e90     int  tcpip!Fl4tPnpEvent+0
   +0x088 UnloadHandler    : (null) 
   +0x090 UninstallHandler : (null) 
   +0x098 RequestCompleteHandler : (null) 
   +0x0a0 StatusHandlerEx  : 0xfffff804`7cfc1fe0     void  tcpip!FlStatus+0
   +0x0a0 StatusHandler    : 0xfffff804`7cfc1fe0     void  tcpip!FlStatus+0
   +0x0a8 StatusCompleteHandler : (null) 
   +0x0b0 ReceiveNetBufferListsHandler : 0xfffff804`7cf96d80     void  tcpip!FlReceiveNetBufferListChain+0
   +0x0b8 SendNetBufferListsCompleteHandler : 0xfffff804`7cf986d0     void  tcpip!FlSendNetBufferListChainComplete+0
   +0x0c0 CoStatusHandlerEx : (null) 
   +0x0c0 CoStatusHandler  : (null) 
   +0x0c8 CoAfRegisterNotifyHandler : (null) 
   +0x0d0 CoReceiveNetBufferListsHandler : (null) 
   +0x0d8 CoSendNetBufferListsCompleteHandler : (null) 
   +0x0e0 OpenAdapterCompleteHandler : (null) 
   +0x0e8 CloseAdapterCompleteHandler : (null) 
   +0x0f0 SendCompleteHandler : (null) 
   +0x0f0 WanSendCompleteHandler : (null) 
   +0x0f8 TransferDataCompleteHandler : (null) 
   +0x0f8 WanTransferDataCompleteHandler : (null) 
   +0x100 ResetCompleteHandler : (null) 
   +0x108 ReceiveHandler   : (null) 
   +0x108 WanReceiveHandler : (null) 
   +0x110 ReceiveCompleteHandler : (null) 
   +0x118 ReceivePacketHandler : (null) 
   +0x120 BindAdapterHandler : (null) 
   +0x128 UnbindAdapterHandler : (null) 
   +0x130 CoSendCompleteHandler : (null) 
   +0x138 CoReceivePacketHandler : (null) 
   +0x140 OidRequestCompleteHandler : 0xfffff804`7cfa6dc0     void  tcpip!FlDirectRequestComplete+0
   +0x148 WorkItem         : _WORK_QUEUE_ITEM
   +0x168 Mutex            : _KMUTANT
   +0x1a0 MutexOwnerThread : (null) 
   +0x1a8 MutexOwnerCount  : 0
   +0x1b0 BindDeviceName   : (null) 
   +0x1b8 RootDeviceName   : (null) 
   +0x1c0 AssociatedMiniDriver : (null) 
   +0x1c8 BindingAdapter   : (null) 
   +0x1d0 DeregEvent       : (null) 
   +0x1d8 ClientChars      : _NDIS_CO_CLIENT_OPTIONAL_HANDLERS
   +0x278 CallMgrChars     : _NDIS_CO_CALL_MANAGER_OPTIONAL_HANDLERS
   +0x308 DirectOidRequestCompleteHandler : 0xfffff804`7cfa6dc0     void  tcpip!FlDirectRequestComplete+0
   +0x310 AllocateSharedMemoryHandler : (null) 
   +0x318 FreeSharedMemoryHandler : (null) 
   +0x320 AllocateSharedMemoryContext : (null) 
   +0x328 ImageName        : _UNICODE_STRING ""
   +0x338 Bind             : KRef<NDIS_BIND_PROTOCOL_DRIVER>
   +0x340 NotifyBindCompleteWorkItem : KCoalescingWorkItem<_NDIS_PROTOCOL_BLOCK>
0: kd> dt 0xffffe108`9c26bb30 _NDIS_PROTOCOL_BLOCK
ndis!_NDIS_PROTOCOL_BLOCK
   +0x000 Header           : _NDIS_OBJECT_HEADER
   +0x008 ProtocolDriverContext : 0xfffff804`7d12ca70 Void
   +0x010 NextProtocol     : 0xffffe108`9c203bb0 _NDIS_PROTOCOL_BLOCK
   +0x018 OpenQueue        : 0xffffe108`9d319aa0 _NDIS_OPEN_BLOCK
   +0x020 Ref              : _REFERENCE_EX
   +0x038 MajorNdisVersion : 0x6 ''
   +0x039 MinorNdisVersion : 0x28 '('
   +0x03a MajorDriverVersion : 0 ''
   +0x03b MinorDriverVersion : 0 ''
   +0x03c Reserved         : 0
   +0x040 Flags            : 0
   +0x048 Name             : _UNICODE_STRING "TCPIP6"
   +0x058 IsIPv4           : 0 ''
   +0x059 IsIPv6           : 0x1 ''
   +0x05a IsNdisTest6      : 0 ''
   +0x060 BindAdapterHandlerEx : 0xfffff804`7cfbff70     int  tcpip!FlBindAdapter+0
   +0x068 UnbindAdapterHandlerEx : 0xfffff804`7cfae5d0     int  tcpip!FlUnbindAdapter+0
   +0x070 OpenAdapterCompleteHandlerEx : 0xfffff804`7d0d1d30     void  tcpip!FlOpenAdapterComplete+0
   +0x078 CloseAdapterCompleteHandlerEx : 0xfffff804`7cfb0420     void  tcpip!FlCloseAdapterComplete+0
   +0x080 PnPEventHandler  : 0xfffff804`7cfc1bf0     int  tcpip!Fl68PnpEvent+0
   +0x080 NetPnPEventHandler : 0xfffff804`7cfc1bf0     int  tcpip!Fl68PnpEvent+0
   +0x088 UnloadHandler    : (null) 
   +0x090 UninstallHandler : (null) 
   +0x098 RequestCompleteHandler : (null) 
   +0x0a0 StatusHandlerEx  : 0xfffff804`7cfc1fe0     void  tcpip!FlStatus+0
   +0x0a0 StatusHandler    : 0xfffff804`7cfc1fe0     void  tcpip!FlStatus+0
   +0x0a8 StatusCompleteHandler : (null) 
   +0x0b0 ReceiveNetBufferListsHandler : 0xfffff804`7cf96d80     void  tcpip!FlReceiveNetBufferListChain+0
   +0x0b8 SendNetBufferListsCompleteHandler : 0xfffff804`7cf986d0     void  tcpip!FlSendNetBufferListChainComplete+0
   +0x0c0 CoStatusHandlerEx : (null) 
   +0x0c0 CoStatusHandler  : (null) 
   +0x0c8 CoAfRegisterNotifyHandler : (null) 
   +0x0d0 CoReceiveNetBufferListsHandler : (null) 
   +0x0d8 CoSendNetBufferListsCompleteHandler : (null) 
   +0x0e0 OpenAdapterCompleteHandler : (null) 
   +0x0e8 CloseAdapterCompleteHandler : (null) 
   +0x0f0 SendCompleteHandler : (null) 
   +0x0f0 WanSendCompleteHandler : (null) 
   +0x0f8 TransferDataCompleteHandler : (null) 
   +0x0f8 WanTransferDataCompleteHandler : (null) 
   +0x100 ResetCompleteHandler : (null) 
   +0x108 ReceiveHandler   : (null) 
   +0x108 WanReceiveHandler : (null) 
   +0x110 ReceiveCompleteHandler : (null) 
   +0x118 ReceivePacketHandler : (null) 
   +0x120 BindAdapterHandler : (null) 
   +0x128 UnbindAdapterHandler : (null) 
   +0x130 CoSendCompleteHandler : (null) 
   +0x138 CoReceivePacketHandler : (null) 
   +0x140 OidRequestCompleteHandler : 0xfffff804`7cfa6dc0     void  tcpip!FlDirectRequestComplete+0
   +0x148 WorkItem         : _WORK_QUEUE_ITEM
   +0x168 Mutex            : _KMUTANT
   +0x1a0 MutexOwnerThread : (null) 
   +0x1a8 MutexOwnerCount  : 0
   +0x1b0 BindDeviceName   : (null) 
   +0x1b8 RootDeviceName   : 0xffffe108`9a80e9c8 _UNICODE_STRING "\DEVICE\{369292E4-DD92-46B9-B680-A71531F1B46E}"
   +0x1c0 AssociatedMiniDriver : (null) 
   +0x1c8 BindingAdapter   : 0xffffe108`9dacf1a0 _NDIS_MINIPORT_BLOCK
   +0x1d0 DeregEvent       : (null) 
   +0x1d8 ClientChars      : _NDIS_CO_CLIENT_OPTIONAL_HANDLERS
   +0x278 CallMgrChars     : _NDIS_CO_CALL_MANAGER_OPTIONAL_HANDLERS
   +0x308 DirectOidRequestCompleteHandler : 0xfffff804`7cfa6dc0     void  tcpip!FlDirectRequestComplete+0
   +0x310 AllocateSharedMemoryHandler : (null) 
   +0x318 FreeSharedMemoryHandler : (null) 
   +0x320 AllocateSharedMemoryContext : (null) 
   +0x328 ImageName        : _UNICODE_STRING "tcpip.sys"
   +0x338 Bind             : KRef<NDIS_BIND_PROTOCOL_DRIVER>
   +0x340 NotifyBindCompleteWorkItem : KCoalescingWorkItem<_NDIS_PROTOCOL_BLOCK>
0: kd> dt 0xffffe108`9c203bb0 _NDIS_PROTOCOL_BLOCK
ndis!_NDIS_PROTOCOL_BLOCK
   +0x000 Header           : _NDIS_OBJECT_HEADER
   +0x008 ProtocolDriverContext : 0xfffff804`7d12cd10 Void
   +0x010 NextProtocol     : (null) 结束了，结束标志。
   +0x018 OpenQueue        : 0xffffe108`9d31aaa0 _NDIS_OPEN_BLOCK
   +0x020 Ref              : _REFERENCE_EX
   +0x038 MajorNdisVersion : 0x6 ''
   +0x039 MinorNdisVersion : 0x28 '('
   +0x03a MajorDriverVersion : 0 ''
   +0x03b MinorDriverVersion : 0 ''
   +0x03c Reserved         : 0
   +0x040 Flags            : 0
   +0x048 Name             : _UNICODE_STRING "TCPIP"
   +0x058 IsIPv4           : 0x1 ''
   +0x059 IsIPv6           : 0 ''
   +0x05a IsNdisTest6      : 0 ''
   +0x060 BindAdapterHandlerEx : 0xfffff804`7cfbff70     int  tcpip!FlBindAdapter+0
   +0x068 UnbindAdapterHandlerEx : 0xfffff804`7cfae5d0     int  tcpip!FlUnbindAdapter+0
   +0x070 OpenAdapterCompleteHandlerEx : 0xfffff804`7d0d1d30     void  tcpip!FlOpenAdapterComplete+0
   +0x078 CloseAdapterCompleteHandlerEx : 0xfffff804`7cfb0420     void  tcpip!FlCloseAdapterComplete+0
   +0x080 PnPEventHandler  : 0xfffff804`7cfc1c20     int  tcpip!Fl48PnpEvent+0
   +0x080 NetPnPEventHandler : 0xfffff804`7cfc1c20     int  tcpip!Fl48PnpEvent+0
   +0x088 UnloadHandler    : (null) 
   +0x090 UninstallHandler : (null) 
   +0x098 RequestCompleteHandler : (null) 
   +0x0a0 StatusHandlerEx  : 0xfffff804`7cfc1fe0     void  tcpip!FlStatus+0
   +0x0a0 StatusHandler    : 0xfffff804`7cfc1fe0     void  tcpip!FlStatus+0
   +0x0a8 StatusCompleteHandler : (null) 
   +0x0b0 ReceiveNetBufferListsHandler : 0xfffff804`7cf96d80     void  tcpip!FlReceiveNetBufferListChain+0
   +0x0b8 SendNetBufferListsCompleteHandler : 0xfffff804`7cf986d0     void  tcpip!FlSendNetBufferListChainComplete+0
   +0x0c0 CoStatusHandlerEx : (null) 
   +0x0c0 CoStatusHandler  : (null) 
   +0x0c8 CoAfRegisterNotifyHandler : (null) 
   +0x0d0 CoReceiveNetBufferListsHandler : (null) 
   +0x0d8 CoSendNetBufferListsCompleteHandler : (null) 
   +0x0e0 OpenAdapterCompleteHandler : (null) 
   +0x0e8 CloseAdapterCompleteHandler : (null) 
   +0x0f0 SendCompleteHandler : (null) 
   +0x0f0 WanSendCompleteHandler : (null) 
   +0x0f8 TransferDataCompleteHandler : (null) 
   +0x0f8 WanTransferDataCompleteHandler : (null) 
   +0x100 ResetCompleteHandler : (null) 
   +0x108 ReceiveHandler   : (null) 
   +0x108 WanReceiveHandler : (null) 
   +0x110 ReceiveCompleteHandler : (null) 
   +0x118 ReceivePacketHandler : (null) 
   +0x120 BindAdapterHandler : (null) 
   +0x128 UnbindAdapterHandler : (null) 
   +0x130 CoSendCompleteHandler : (null) 
   +0x138 CoReceivePacketHandler : (null) 
   +0x140 OidRequestCompleteHandler : 0xfffff804`7cfa6dc0     void  tcpip!FlDirectRequestComplete+0
   +0x148 WorkItem         : _WORK_QUEUE_ITEM
   +0x168 Mutex            : _KMUTANT
   +0x1a0 MutexOwnerThread : (null) 
   +0x1a8 MutexOwnerCount  : 0
   +0x1b0 BindDeviceName   : (null) 
   +0x1b8 RootDeviceName   : 0xffffe108`9a80e9c8 _UNICODE_STRING "\DEVICE\{369292E4-DD92-46B9-B680-A71531F1B46E}"
   +0x1c0 AssociatedMiniDriver : (null) 
   +0x1c8 BindingAdapter   : 0xffffe108`9dacf1a0 _NDIS_MINIPORT_BLOCK
   +0x1d0 DeregEvent       : (null) 
   +0x1d8 ClientChars      : _NDIS_CO_CLIENT_OPTIONAL_HANDLERS
   +0x278 CallMgrChars     : _NDIS_CO_CALL_MANAGER_OPTIONAL_HANDLERS
   +0x308 DirectOidRequestCompleteHandler : 0xfffff804`7cfa6dc0     void  tcpip!FlDirectRequestComplete+0
   +0x310 AllocateSharedMemoryHandler : (null) 
   +0x318 FreeSharedMemoryHandler : (null) 
   +0x320 AllocateSharedMemoryContext : (null) 
   +0x328 ImageName        : _UNICODE_STRING "tcpip.sys"
   +0x338 Bind             : KRef<NDIS_BIND_PROTOCOL_DRIVER>
   +0x340 NotifyBindCompleteWorkItem : KCoalescingWorkItem<_NDIS_PROTOCOL_BLOCK>
```

接下来用命令验证下：

```plain
0: kd> !ndiskd.protocol
ffffe1089a179010 - WANARPV6

ffffe1089a1a5aa0 - WANARP

ffffe1089de60ae0 - RSPNDR
  ffffe1089dde9aa0 - Intel(R) 82574L Gigabit Network Connection
  ffffe1089ddeeaa0 - Bluetooth Device (Personal Area Network)

ffffe1089a16eb30 - MSLLDP
  ffffe1089ddeaaa0 - Intel(R) 82574L Gigabit Network Connection

ffffe1089a16cb30 - LLTDIO
  ffffe1089ddebaa0 - Bluetooth Device (Personal Area Network)
  ffffe1089ddef010 - Intel(R) 82574L Gigabit Network Connection

ffffe1089c4998a0 - RDMANDK

ffffe1089c27c8a0 - TCPIP6TUNNEL

ffffe1089c297430 - TCPIPTUNNEL

ffffe1089c26bb30 - TCPIP6
  ffffe1089d319aa0 - Bluetooth Device (Personal Area Network)
  ffffe1089c636480 - Intel(R) 82574L Gigabit Network Connection

ffffe1089c203bb0 - TCPIP
  ffffe1089d31aaa0 - Bluetooth Device (Personal Area Network)
  ffffe1089c35b010 - Intel(R) 82574L Gigabit Network Connection
```

再用命令查看下每个协议的具体的信息：

```plain
0: kd> !ndiskd.protocol ffffe1089a179010


PROTOCOL

    WANARPV6

    Ndis handle        ffffe1089a179010
    Ndis API version   v6.85
    Driver context     fffff8048f988250
    Driver version     v0.0
    Reference count    1
    Flags              [No flags set]
    Driver image       wanarp.sys


BINDINGS

    Open               Miniport            Miniport Name                        
    There are no open bindings to this protocol


HANDLERS

    Protocol handler                       Function pointer   Symbol (if available)
    BindAdapterHandlerEx                   fffff8048f9831f0  bp wanarp!WanNdisBindAdapter
    UnbindAdapterHandlerEx                 fffff8048f997530  bp wanarp!WanNdisUnbindAdapter
    OpenAdapterCompleteHandlerEx           fffff8048f997390  bp wanarp!WanNdisOpenAdapterComplete
    CloseAdapterCompleteHandlerEx          fffff8048f9972d0  bp wanarp!WanNdisCloseAdapterComplete
    NetPnPEventHandler                     fffff8048f996ed0  bp wanarp!WanNdisPnPEvent
    UninstallHandler                       [None]
    SendNetBufferListsCompleteHandler      fffff8048f981780  bp wanarp!WanNdisSendComplete
    ReceiveNetBufferListsHandler           fffff8048f981010  bp wanarp!WanNdisReceivePackets
    StatusHandlerEx                        fffff8048f981c80  bp wanarp!WanNdisStatus
    OidRequestCompleteHandler              fffff8048f983370  bp wanarp!WanNdisRequestComplete
    DirectOidRequestCompleteHandler        [None]
0: kd> !ndiskd.protocol ffffe1089a1a5aa0


PROTOCOL

    WANARP

    Ndis handle        ffffe1089a1a5aa0
    Ndis API version   v6.85
    Driver context     fffff8048f988000
    Driver version     v0.0
    Reference count    1
    Flags              [No flags set]
    Driver image       wanarp.sys


BINDINGS

    Open               Miniport            Miniport Name                        
    There are no open bindings to this protocol


HANDLERS

    Protocol handler                       Function pointer   Symbol (if available)
    BindAdapterHandlerEx                   fffff8048f9831f0  bp wanarp!WanNdisBindAdapter
    UnbindAdapterHandlerEx                 fffff8048f997530  bp wanarp!WanNdisUnbindAdapter
    OpenAdapterCompleteHandlerEx           fffff8048f997390  bp wanarp!WanNdisOpenAdapterComplete
    CloseAdapterCompleteHandlerEx          fffff8048f9972d0  bp wanarp!WanNdisCloseAdapterComplete
    NetPnPEventHandler                     fffff8048f996ed0  bp wanarp!WanNdisPnPEvent
    UninstallHandler                       [None]
    SendNetBufferListsCompleteHandler      fffff8048f981780  bp wanarp!WanNdisSendComplete
    ReceiveNetBufferListsHandler           fffff8048f981010  bp wanarp!WanNdisReceivePackets
    StatusHandlerEx                        fffff8048f981c80  bp wanarp!WanNdisStatus
    OidRequestCompleteHandler              fffff8048f983370  bp wanarp!WanNdisRequestComplete
    DirectOidRequestCompleteHandler        [None]
0: kd> !ndiskd.protocol ffffe1089de60ae0


PROTOCOL

    RSPNDR

    Ndis handle        ffffe1089de60ae0
    Ndis API version   v6.30
    Driver context     NULL
    Driver version     v0.0
    Reference count    3
    Flags              [No flags set]
    Driver image       rspndr.sys


BINDINGS

    Open               Miniport            Miniport Name                        
    ffffe1089dde9aa0   ffffe1089c5e81a0    Intel(R) 82574L Gigabit Network Connection
    ffffe1089ddeeaa0   ffffe1089dacf1a0    Bluetooth Device (Personal Area Network)


HANDLERS

    Protocol handler                       Function pointer   Symbol (if available)
    BindAdapterHandlerEx                   fffff8048f961260  bp rspndr!ToppBindAdapterHandlerEx
    UnbindAdapterHandlerEx                 fffff8048f964a40  bp rspndr!ToppUnbindAdapterHandlerEx
    OpenAdapterCompleteHandlerEx           fffff8048f9644a0  bp rspndr!ToppOpenAdapterCompleteHandlerEx
    CloseAdapterCompleteHandlerEx          fffff8048f964460  bp rspndr!ToppCloseAdapterCompleteHandlerEx
    NetPnPEventHandler                     fffff8048f962040  bp rspndr!ToppPnPEventHandler
    UninstallHandler                       [None]
    SendNetBufferListsCompleteHandler      fffff8048f9649c0  bp rspndr!ToppSendNetBufferListsCompleteHandler
    ReceiveNetBufferListsHandler           fffff8048f9644d0  bp rspndr!ToppReceiveNetBufferListHandler
    StatusHandlerEx                        fffff8048f961010  bp rspndr!ToppStatusHandlerEx
    OidRequestCompleteHandler              fffff8048f962140  bp rspndr!ToppOidRequestCompleteHandler
    DirectOidRequestCompleteHandler        [None]
0: kd> !ndiskd.protocol ffffe1089a16eb30


PROTOCOL

    MSLLDP

    Ndis handle        ffffe1089a16eb30
    Ndis API version   v6.30
    Driver context     fffff8048f949220
    Driver version     v10.0
    Reference count    2
    Flags              [No flags set]
    Driver image       mslldp.sys


BINDINGS

    Open               Miniport            Miniport Name                        
    ffffe1089ddeaaa0   ffffe1089c5e81a0    Intel(R) 82574L Gigabit Network Connection


HANDLERS

    Protocol handler                       Function pointer   Symbol (if available)
    BindAdapterHandlerEx                   fffff8048f94ca70  bp mslldp!lldpProtBindAdapter
    UnbindAdapterHandlerEx                 fffff8048f94d170  bp mslldp!lldpProtUnbindAdapter
    OpenAdapterCompleteHandlerEx           fffff8048f94cf80  bp mslldp!lldpProtOpenAdapterComplete
    CloseAdapterCompleteHandlerEx          fffff8048f94cc20  bp mslldp!lldpProtCloseAdapterComplete
    NetPnPEventHandler                     fffff8048f94cc40  bp mslldp!lldpProtNetPnPEvent
    UninstallHandler                       [None]
    SendNetBufferListsCompleteHandler      fffff8048f942a50  bp mslldp!lldpProtSendNetBufferListsComplete
    ReceiveNetBufferListsHandler           fffff8048f941010  bp mslldp!lldpProtReceiveNetBufferLists
    StatusHandlerEx                        fffff8048f942a90  bp mslldp!lldpProtStatus
    OidRequestCompleteHandler              fffff8048f942a20  bp mslldp!lldpProtOidRequestComplete
    DirectOidRequestCompleteHandler        [None]
0: kd> !ndiskd.protocol ffffe1089a16cb30


PROTOCOL

    LLTDIO

    Ndis handle        ffffe1089a16cb30
    Ndis API version   v6.30
    Driver context     NULL
    Driver version     v0.0
    Reference count    3
    Flags              [No flags set]
    Driver image       lltdio.sys


BINDINGS

    Open               Miniport            Miniport Name                        
    ffffe1089ddebaa0   ffffe1089dacf1a0    Bluetooth Device (Personal Area Network)
    ffffe1089ddef010   ffffe1089c5e81a0    Intel(R) 82574L Gigabit Network Connection


HANDLERS

    Protocol handler                       Function pointer   Symbol (if available)
    BindAdapterHandlerEx                   fffff8048f9214d0  bp lltdio!ToppBindAdapterHandlerEx
    UnbindAdapterHandlerEx                 fffff8048f923c90  bp lltdio!ToppUnbindAdapterHandlerEx
    OpenAdapterCompleteHandlerEx           fffff8048f9236d0  bp lltdio!ToppOpenAdapterCompleteHandlerEx
    CloseAdapterCompleteHandlerEx          fffff8048f923680  bp lltdio!ToppCloseAdapterCompleteHandlerEx
    NetPnPEventHandler                     fffff8048f921c20  bp lltdio!ToppPnPEventHandler
    UninstallHandler                       [None]
    SendNetBufferListsCompleteHandler      fffff8048f923bd0  bp lltdio!ToppSendNetBufferListsCompleteHandler
    ReceiveNetBufferListsHandler           fffff8048f923700  bp lltdio!ToppReceiveNetBufferListHandler
    StatusHandlerEx                        fffff8048f921e00  bp lltdio!ToppStatusHandlerEx
    OidRequestCompleteHandler              fffff8048f921e90  bp lltdio!TopOidRequestCompleteHandler
    DirectOidRequestCompleteHandler        [None]
0: kd> !ndiskd.protocol ffffe1089c4998a0


PROTOCOL

    RDMANDK

    Ndis handle        ffffe1089c4998a0
    Ndis API version   v6.40
    Driver context     fffff8047d12cfb0
    Driver version     v0.0
    Reference count    1
    Flags              [No flags set]
    Driver image       [Not available]     Why not?


BINDINGS

    Open               Miniport            Miniport Name                        
    There are no open bindings to this protocol


HANDLERS

    Protocol handler                       Function pointer   Symbol (if available)
    BindAdapterHandlerEx                   fffff8047cfc7f80  bp tcpip!FlRdmaBindAdapter
    UnbindAdapterHandlerEx                 fffff8047d0db690  bp tcpip!FlRdmaUnbindAdapter
    OpenAdapterCompleteHandlerEx           fffff8047d0d1d30  bp tcpip!FlOpenAdapterComplete
    CloseAdapterCompleteHandlerEx          fffff8047cfb0420  bp tcpip!FlCloseAdapterComplete
    NetPnPEventHandler                     fffff8047cfc7a60  bp tcpip!FlRdmaPnpEvent
    UninstallHandler                       [None]
    SendNetBufferListsCompleteHandler      fffff8047cfab520  bp tcpip!Fl4lCleanup
    ReceiveNetBufferListsHandler           fffff8047cfab520  bp tcpip!Fl4lCleanup
    StatusHandlerEx                        fffff8047cfab520  bp tcpip!Fl4lCleanup
    OidRequestCompleteHandler              fffff8047cfa6dc0  bp tcpip!FlDirectRequestComplete
    DirectOidRequestCompleteHandler        fffff8047cfa6dc0  bp tcpip!FlDirectRequestComplete
0: kd> !ndiskd.protocol ffffe1089c27c8a0


PROTOCOL

    TCPIP6TUNNEL

    Ndis handle        ffffe1089c27c8a0
    Ndis API version   v6.40
    Driver context     fffff8047d132ec0
    Driver version     v0.0
    Reference count    1
    Flags              [No flags set]
    Driver image       [Not available]     Why not?


BINDINGS

    Open               Miniport            Miniport Name                        
    There are no open bindings to this protocol


HANDLERS

    Protocol handler                       Function pointer   Symbol (if available)
    BindAdapterHandlerEx                   fffff8047cfbff70  bp tcpip!FlBindAdapter
    UnbindAdapterHandlerEx                 fffff8047cfae5d0  bp tcpip!FlUnbindAdapter
    OpenAdapterCompleteHandlerEx           fffff8047d0d1d30  bp tcpip!FlOpenAdapterComplete
    CloseAdapterCompleteHandlerEx          fffff8047cfb0420  bp tcpip!FlCloseAdapterComplete
    NetPnPEventHandler                     fffff8047cfe2e60  bp tcpip!Fl6tPnpEvent
    UninstallHandler                       [None]
    SendNetBufferListsCompleteHandler      fffff8047cf986d0  bp tcpip!FlSendNetBufferListChainComplete
    ReceiveNetBufferListsHandler           fffff8047cf96d80  bp tcpip!FlReceiveNetBufferListChain
    StatusHandlerEx                        fffff8047cfc1fe0  bp tcpip!FlStatus
    OidRequestCompleteHandler              fffff8047cfa6dc0  bp tcpip!FlDirectRequestComplete
    DirectOidRequestCompleteHandler        fffff8047cfa6dc0  bp tcpip!FlDirectRequestComplete
0: kd> !ndiskd.protocol ffffe1089c297430


PROTOCOL

    TCPIPTUNNEL

    Ndis handle        ffffe1089c297430
    Ndis API version   v6.40
    Driver context     fffff8047d132c20
    Driver version     v0.0
    Reference count    1
    Flags              [No flags set]
    Driver image       [Not available]     Why not?


BINDINGS

    Open               Miniport            Miniport Name                        
    There are no open bindings to this protocol


HANDLERS

    Protocol handler                       Function pointer   Symbol (if available)
    BindAdapterHandlerEx                   fffff8047cfbff70  bp tcpip!FlBindAdapter
    UnbindAdapterHandlerEx                 fffff8047cfae5d0  bp tcpip!FlUnbindAdapter
    OpenAdapterCompleteHandlerEx           fffff8047d0d1d30  bp tcpip!FlOpenAdapterComplete
    CloseAdapterCompleteHandlerEx          fffff8047cfb0420  bp tcpip!FlCloseAdapterComplete
    NetPnPEventHandler                     fffff8047cfe2e90  bp tcpip!Fl4tPnpEvent
    UninstallHandler                       [None]
    SendNetBufferListsCompleteHandler      fffff8047cf986d0  bp tcpip!FlSendNetBufferListChainComplete
    ReceiveNetBufferListsHandler           fffff8047cf96d80  bp tcpip!FlReceiveNetBufferListChain
    StatusHandlerEx                        fffff8047cfc1fe0  bp tcpip!FlStatus
    OidRequestCompleteHandler              fffff8047cfa6dc0  bp tcpip!FlDirectRequestComplete
    DirectOidRequestCompleteHandler        fffff8047cfa6dc0  bp tcpip!FlDirectRequestComplete
0: kd> !ndiskd.protocol ffffe1089c26bb30


PROTOCOL

    TCPIP6

    Ndis handle        ffffe1089c26bb30
    Ndis API version   v6.40
    Driver context     fffff8047d12ca70
    Driver version     v0.0
    Reference count    3
    Flags              [No flags set]
    Driver image       tcpip.sys


BINDINGS

    Open               Miniport            Miniport Name                        
    ffffe1089d319aa0   ffffe1089dacf1a0    Bluetooth Device (Personal Area Network)
    ffffe1089c636480   ffffe1089c5e81a0    Intel(R) 82574L Gigabit Network Connection


HANDLERS

    Protocol handler                       Function pointer   Symbol (if available)
    BindAdapterHandlerEx                   fffff8047cfbff70  bp tcpip!FlBindAdapter
    UnbindAdapterHandlerEx                 fffff8047cfae5d0  bp tcpip!FlUnbindAdapter
    OpenAdapterCompleteHandlerEx           fffff8047d0d1d30  bp tcpip!FlOpenAdapterComplete
    CloseAdapterCompleteHandlerEx          fffff8047cfb0420  bp tcpip!FlCloseAdapterComplete
    NetPnPEventHandler                     fffff8047cfc1bf0  bp tcpip!Fl68PnpEvent
    UninstallHandler                       [None]
    SendNetBufferListsCompleteHandler      fffff8047cf986d0  bp tcpip!FlSendNetBufferListChainComplete
    ReceiveNetBufferListsHandler           fffff8047cf96d80  bp tcpip!FlReceiveNetBufferListChain
    StatusHandlerEx                        fffff8047cfc1fe0  bp tcpip!FlStatus
    OidRequestCompleteHandler              fffff8047cfa6dc0  bp tcpip!FlDirectRequestComplete
    DirectOidRequestCompleteHandler        fffff8047cfa6dc0  bp tcpip!FlDirectRequestComplete
0: kd> !ndiskd.protocol ffffe1089c203bb0


PROTOCOL

    TCPIP

    Ndis handle        ffffe1089c203bb0
    Ndis API version   v6.40
    Driver context     fffff8047d12cd10
    Driver version     v0.0
    Reference count    3
    Flags              [No flags set]
    Driver image       tcpip.sys


BINDINGS

    Open               Miniport            Miniport Name                        
    ffffe1089d31aaa0   ffffe1089dacf1a0    Bluetooth Device (Personal Area Network)
    ffffe1089c35b010   ffffe1089c5e81a0    Intel(R) 82574L Gigabit Network Connection


HANDLERS

    Protocol handler                       Function pointer   Symbol (if available)
    BindAdapterHandlerEx                   fffff8047cfbff70  bp tcpip!FlBindAdapter
    UnbindAdapterHandlerEx                 fffff8047cfae5d0  bp tcpip!FlUnbindAdapter
    OpenAdapterCompleteHandlerEx           fffff8047d0d1d30  bp tcpip!FlOpenAdapterComplete
    CloseAdapterCompleteHandlerEx          fffff8047cfb0420  bp tcpip!FlCloseAdapterComplete
    NetPnPEventHandler                     fffff8047cfc1c20  bp tcpip!Fl48PnpEvent
    UninstallHandler                       [None]
    SendNetBufferListsCompleteHandler      fffff8047cf986d0  bp tcpip!FlSendNetBufferListChainComplete
    ReceiveNetBufferListsHandler           fffff8047cf96d80  bp tcpip!FlReceiveNetBufferListChain
    StatusHandlerEx                        fffff8047cfc1fe0  bp tcpip!FlStatus
    OidRequestCompleteHandler              fffff8047cfa6dc0  bp tcpip!FlDirectRequestComplete
    DirectOidRequestCompleteHandler        fffff8047cfa6dc0  bp tcpip!FlDirectRequestComplete
```

本工程的都是要以编程的方式实现!ndiskd.protocol命令（包括带参数的和不带参数的）并输出给用户看看。

## 编码实现

代码如下：

```plain
#include "ProtocolDriver.h" //这里有结构的定义。


PKSPIN_LOCK ndisProtocolListLock;//ndis.sys定义的是结构，这里定义的是指针。测试时，可赋予x ndis!ndisProtocolListLock的值。
_NDIS_PROTOCOL_BLOCK * ndisProtocolList;//测试的时候可以赋予dq ndis!ndisProtocolList L1的值。


void DumpOneProtocolDriverInfo(_NDIS_PROTOCOL_BLOCK * ProtocolDriver)
{
    Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "Name:%wZ", ProtocolDriver->Name);
    Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "BindDeviceName:%wZ", ProtocolDriver->BindDeviceName);
    Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "RootDeviceName:%wZ", ProtocolDriver->RootDeviceName);
    Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "ImageName:%wZ", ProtocolDriver->ImageName);

    Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "BindAdapterHandlerEx:%p", ProtocolDriver->BindAdapterHandlerEx);//PNDIS_PROTOCOL_DRIVER_CHARACTERISTICS传递过来的。
    Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "UnbindAdapterHandlerEx:%p", ProtocolDriver->UnbindAdapterHandlerEx);//PNDIS_PROTOCOL_DRIVER_CHARACTERISTICS传递过来的。
    Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "OpenAdapterCompleteHandlerEx:%p", ProtocolDriver->OpenAdapterCompleteHandlerEx);//PNDIS_PROTOCOL_DRIVER_CHARACTERISTICS传递过来的。
    Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "CloseAdapterCompleteHandlerEx:%p", ProtocolDriver->CloseAdapterCompleteHandlerEx);//PNDIS_PROTOCOL_DRIVER_CHARACTERISTICS传递过来的。

    Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "PnPEventHandler/NetPnPEventHandler:%p", ProtocolDriver->PnPEventHandler);//PNDIS_PROTOCOL_DRIVER_CHARACTERISTICS传递过来的。

    //Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "UnloadHandler:%p", ProtocolDriver->UnloadHandler);//可以考虑不显示。
    Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "UninstallHandler:%p", ProtocolDriver->UninstallHandler);//PNDIS_PROTOCOL_DRIVER_CHARACTERISTICS传递过来的。
    //Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "RequestCompleteHandler:%p", ProtocolDriver->RequestCompleteHandler);//可以考虑不显示。

    Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "StatusHandler/StatusHandlerEx:%p", ProtocolDriver->StatusHandler);//PNDIS_PROTOCOL_DRIVER_CHARACTERISTICS传递过来的。

    //Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "StatusCompleteHandler:%p", ProtocolDriver->StatusCompleteHandler);//可以考虑不显示。
    Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "ReceiveNetBufferListsHandler:%p", ProtocolDriver->ReceiveNetBufferListsHandler);//PNDIS_PROTOCOL_DRIVER_CHARACTERISTICS传递过来的。
    Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "SendNetBufferListsCompleteHandler:%p", ProtocolDriver->SendNetBufferListsCompleteHandler);//PNDIS_PROTOCOL_DRIVER_CHARACTERISTICS传递过来的。

    //Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "CoStatusHandler/CoStatusHandlerEx:%p", ProtocolDriver->CoStatusHandler);//可以考虑不显示。

    //Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "CoAfRegisterNotifyHandler:%p", ProtocolDriver->CoAfRegisterNotifyHandler);//可以考虑不显示。
    //Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "CoReceiveNetBufferListsHandler:%p", ProtocolDriver->CoReceiveNetBufferListsHandler);//可以考虑不显示。
    //Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "CoSendNetBufferListsCompleteHandler:%p", ProtocolDriver->CoSendNetBufferListsCompleteHandler);//可以考虑不显示。
    //Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "OpenAdapterCompleteHandler:%p", ProtocolDriver->OpenAdapterCompleteHandler);//可以考虑不显示。
    //Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "CloseAdapterCompleteHandler:%p", ProtocolDriver->CloseAdapterCompleteHandler);//可以考虑不显示。

    //Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "SendCompleteHandler/WanSendCompleteHandler:%p", ProtocolDriver->SendCompleteHandler);//可以考虑不显示。
    //Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "TransferDataCompleteHandler/WanTransferDataCompleteHandler:%p", ProtocolDriver->TransferDataCompleteHandler);//可以考虑不显示。

    //Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "ResetCompleteHandler:%p", ProtocolDriver->ResetCompleteHandler);//可以考虑不显示。

    //Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "ReceiveHandler/WanReceiveHandler:%p", ProtocolDriver->ReceiveHandler);//可以考虑不显示。

    //Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "ReceiveCompleteHandler:%p", ProtocolDriver->ReceiveCompleteHandler);//可以考虑不显示。
    //Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "ReceivePacketHandler:%p", ProtocolDriver->ReceivePacketHandler);//可以考虑不显示。
    //Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "BindAdapterHandler:%p", ProtocolDriver->BindAdapterHandler);//可以考虑不显示。
    //Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "UnbindAdapterHandler:%p", ProtocolDriver->UnbindAdapterHandler);//可以考虑不显示。
    //Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "CoSendCompleteHandler:%p", ProtocolDriver->CoSendCompleteHandler);//可以考虑不显示。
    //Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "CoReceivePacketHandler:%p", ProtocolDriver->CoReceivePacketHandler);//可以考虑不显示。
    Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "OidRequestCompleteHandler:%p", ProtocolDriver->OidRequestCompleteHandler);//PNDIS_PROTOCOL_DRIVER_CHARACTERISTICS传递过来的。

    Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "DirectOidRequestCompleteHandler:%p", ProtocolDriver->DirectOidRequestCompleteHandler);//PNDIS_PROTOCOL_DRIVER_CHARACTERISTICS传递过来的。
    //Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "AllocateSharedMemoryHandler:%p", ProtocolDriver->AllocateSharedMemoryHandler);//可以考虑不显示。
    //Print(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "FreeSharedMemoryHandler:%p", ProtocolDriver->FreeSharedMemoryHandler);//可以考虑不显示。

    //ClientChars和CallMgrChars里的信息都不打印了。

    //AssociatedMiniDriver和BindingAdapter的信息都不打印了。

    DbgPrintEx(DPFLTR_DEFAULT_ID, DPFLTR_INFO_LEVEL, "\r\n");
}


void DumpProtocolDriverInfo()
{
    if (!ndisProtocolList || !ndisProtocolListLock) {
        return;
    }

    KIRQL Irql = KeAcquireSpinLockRaiseToDpc(ndisProtocolListLock);
    for (_NDIS_PROTOCOL_BLOCK * Tmp = ndisProtocolList; Tmp; Tmp = Tmp->NextProtocol) {
        DumpOneProtocolDriverInfo(Tmp);
    }
    KeReleaseSpinLock(ndisProtocolListLock, Irql);
}
```

测试的效果如下：

```plain
0: kd> g
FILE:ProtocolDriver.cpp, LINE:10, Name:WANARPV6.
FILE:ProtocolDriver.cpp, LINE:11, BindDeviceName:(null).
FILE:ProtocolDriver.cpp, LINE:12, RootDeviceName:(null).
FILE:ProtocolDriver.cpp, LINE:13, ImageName:wanarp.sys.
FILE:ProtocolDriver.cpp, LINE:15, BindAdapterHandlerEx:FFFFF8048F9831F0.
FILE:ProtocolDriver.cpp, LINE:16, UnbindAdapterHandlerEx:FFFFF8048F997530.
FILE:ProtocolDriver.cpp, LINE:17, OpenAdapterCompleteHandlerEx:FFFFF8048F997390.
FILE:ProtocolDriver.cpp, LINE:18, CloseAdapterCompleteHandlerEx:FFFFF8048F9972D0.
FILE:ProtocolDriver.cpp, LINE:20, PnPEventHandler/NetPnPEventHandler:FFFFF8048F996ED0.
FILE:ProtocolDriver.cpp, LINE:23, UninstallHandler:0000000000000000.
FILE:ProtocolDriver.cpp, LINE:26, StatusHandler/StatusHandlerEx:FFFFF8048F981C80.
FILE:ProtocolDriver.cpp, LINE:29, ReceiveNetBufferListsHandler:FFFFF8048F981010.
FILE:ProtocolDriver.cpp, LINE:30, SendNetBufferListsCompleteHandler:FFFFF8048F981780.
FILE:ProtocolDriver.cpp, LINE:53, OidRequestCompleteHandler:FFFFF8048F983370.
FILE:ProtocolDriver.cpp, LINE:55, DirectOidRequestCompleteHandler:0000000000000000.

FILE:ProtocolDriver.cpp, LINE:10, Name:WANARP.
FILE:ProtocolDriver.cpp, LINE:11, BindDeviceName:(null).
FILE:ProtocolDriver.cpp, LINE:12, RootDeviceName:(null).
FILE:ProtocolDriver.cpp, LINE:13, ImageName:wanarp.sys.
FILE:ProtocolDriver.cpp, LINE:15, BindAdapterHandlerEx:FFFFF8048F9831F0.
FILE:ProtocolDriver.cpp, LINE:16, UnbindAdapterHandlerEx:FFFFF8048F997530.
FILE:ProtocolDriver.cpp, LINE:17, OpenAdapterCompleteHandlerEx:FFFFF8048F997390.
FILE:ProtocolDriver.cpp, LINE:18, CloseAdapterCompleteHandlerEx:FFFFF8048F9972D0.
FILE:ProtocolDriver.cpp, LINE:20, PnPEventHandler/NetPnPEventHandler:FFFFF8048F996ED0.
FILE:ProtocolDriver.cpp, LINE:23, UninstallHandler:0000000000000000.
FILE:ProtocolDriver.cpp, LINE:26, StatusHandler/StatusHandlerEx:FFFFF8048F981C80.
FILE:ProtocolDriver.cpp, LINE:29, ReceiveNetBufferListsHandler:FFFFF8048F981010.
FILE:ProtocolDriver.cpp, LINE:30, SendNetBufferListsCompleteHandler:FFFFF8048F981780.
FILE:ProtocolDriver.cpp, LINE:53, OidRequestCompleteHandler:FFFFF8048F983370.
FILE:ProtocolDriver.cpp, LINE:55, DirectOidRequestCompleteHandler:0000000000000000.

FILE:ProtocolDriver.cpp, LINE:10, Name:RSPNDR.
FILE:ProtocolDriver.cpp, LINE:11, BindDeviceName:(null).
FILE:ProtocolDriver.cpp, LINE:12, RootDeviceName:\DEVICE\{65174C02-ADC6-4292-B214-E79177770A8E}.
FILE:ProtocolDriver.cpp, LINE:13, ImageName:rspndr.sys.
FILE:ProtocolDriver.cpp, LINE:15, BindAdapterHandlerEx:FFFFF8048F961260.
FILE:ProtocolDriver.cpp, LINE:16, UnbindAdapterHandlerEx:FFFFF8048F964A40.
FILE:ProtocolDriver.cpp, LINE:17, OpenAdapterCompleteHandlerEx:FFFFF8048F9644A0.
FILE:ProtocolDriver.cpp, LINE:18, CloseAdapterCompleteHandlerEx:FFFFF8048F964460.
FILE:ProtocolDriver.cpp, LINE:20, PnPEventHandler/NetPnPEventHandler:FFFFF8048F962040.
FILE:ProtocolDriver.cpp, LINE:23, UninstallHandler:0000000000000000.
FILE:ProtocolDriver.cpp, LINE:26, StatusHandler/StatusHandlerEx:FFFFF8048F961010.
FILE:ProtocolDriver.cpp, LINE:29, ReceiveNetBufferListsHandler:FFFFF8048F9644D0.
FILE:ProtocolDriver.cpp, LINE:30, SendNetBufferListsCompleteHandler:FFFFF8048F9649C0.
FILE:ProtocolDriver.cpp, LINE:53, OidRequestCompleteHandler:FFFFF8048F962140.
FILE:ProtocolDriver.cpp, LINE:55, DirectOidRequestCompleteHandler:0000000000000000.

FILE:ProtocolDriver.cpp, LINE:10, Name:MSLLDP.
FILE:ProtocolDriver.cpp, LINE:11, BindDeviceName:(null).
FILE:ProtocolDriver.cpp, LINE:12, RootDeviceName:\DEVICE\{65174C02-ADC6-4292-B214-E79177770A8E}.
FILE:ProtocolDriver.cpp, LINE:13, ImageName:mslldp.sys.
FILE:ProtocolDriver.cpp, LINE:15, BindAdapterHandlerEx:FFFFF8048F94CA70.
FILE:ProtocolDriver.cpp, LINE:16, UnbindAdapterHandlerEx:FFFFF8048F94D170.
FILE:ProtocolDriver.cpp, LINE:17, OpenAdapterCompleteHandlerEx:FFFFF8048F94CF80.
FILE:ProtocolDriver.cpp, LINE:18, CloseAdapterCompleteHandlerEx:FFFFF8048F94CC20.
FILE:ProtocolDriver.cpp, LINE:20, PnPEventHandler/NetPnPEventHandler:FFFFF8048F94CC40.
FILE:ProtocolDriver.cpp, LINE:23, UninstallHandler:0000000000000000.
FILE:ProtocolDriver.cpp, LINE:26, StatusHandler/StatusHandlerEx:FFFFF8048F942A90.
FILE:ProtocolDriver.cpp, LINE:29, ReceiveNetBufferListsHandler:FFFFF8048F941010.
FILE:ProtocolDriver.cpp, LINE:30, SendNetBufferListsCompleteHandler:FFFFF8048F942A50.
FILE:ProtocolDriver.cpp, LINE:53, OidRequestCompleteHandler:FFFFF8048F942A20.
FILE:ProtocolDriver.cpp, LINE:55, DirectOidRequestCompleteHandler:0000000000000000.

FILE:ProtocolDriver.cpp, LINE:10, Name:LLTDIO.
FILE:ProtocolDriver.cpp, LINE:11, BindDeviceName:(null).
FILE:ProtocolDriver.cpp, LINE:12, RootDeviceName:\DEVICE\{369292E4-DD92-46B9-B680-A71531F1B46E}.
FILE:ProtocolDriver.cpp, LINE:13, ImageName:lltdio.sys.
FILE:ProtocolDriver.cpp, LINE:15, BindAdapterHandlerEx:FFFFF8048F9214D0.
FILE:ProtocolDriver.cpp, LINE:16, UnbindAdapterHandlerEx:FFFFF8048F923C90.
FILE:ProtocolDriver.cpp, LINE:17, OpenAdapterCompleteHandlerEx:FFFFF8048F9236D0.
FILE:ProtocolDriver.cpp, LINE:18, CloseAdapterCompleteHandlerEx:FFFFF8048F923680.
FILE:ProtocolDriver.cpp, LINE:20, PnPEventHandler/NetPnPEventHandler:FFFFF8048F921C20.
FILE:ProtocolDriver.cpp, LINE:23, UninstallHandler:0000000000000000.
FILE:ProtocolDriver.cpp, LINE:26, StatusHandler/StatusHandlerEx:FFFFF8048F921E00.
FILE:ProtocolDriver.cpp, LINE:29, ReceiveNetBufferListsHandler:FFFFF8048F923700.
FILE:ProtocolDriver.cpp, LINE:30, SendNetBufferListsCompleteHandler:FFFFF8048F923BD0.
FILE:ProtocolDriver.cpp, LINE:53, OidRequestCompleteHandler:FFFFF8048F921E90.
FILE:ProtocolDriver.cpp, LINE:55, DirectOidRequestCompleteHandler:0000000000000000.

FILE:ProtocolDriver.cpp, LINE:10, Name:RDMANDK.
FILE:ProtocolDriver.cpp, LINE:11, BindDeviceName:\DEVICE\{369292E4-DD92-46B9-B680-A71531F1B46E}.
FILE:ProtocolDriver.cpp, LINE:12, RootDeviceName:\DEVICE\{369292E4-DD92-46B9-B680-A71531F1B46E}.
FILE:ProtocolDriver.cpp, LINE:13, ImageName:(null).
FILE:ProtocolDriver.cpp, LINE:15, BindAdapterHandlerEx:FFFFF8047CFC7F80.
FILE:ProtocolDriver.cpp, LINE:16, UnbindAdapterHandlerEx:FFFFF8047D0DB690.
FILE:ProtocolDriver.cpp, LINE:17, OpenAdapterCompleteHandlerEx:FFFFF8047D0D1D30.
FILE:ProtocolDriver.cpp, LINE:18, CloseAdapterCompleteHandlerEx:FFFFF8047CFB0420.
FILE:ProtocolDriver.cpp, LINE:20, PnPEventHandler/NetPnPEventHandler:FFFFF8047CFC7A60.
FILE:ProtocolDriver.cpp, LINE:23, UninstallHandler:0000000000000000.
FILE:ProtocolDriver.cpp, LINE:26, StatusHandler/StatusHandlerEx:FFFFF8047CFAB520.
FILE:ProtocolDriver.cpp, LINE:29, ReceiveNetBufferListsHandler:FFFFF8047CFAB520.
FILE:ProtocolDriver.cpp, LINE:30, SendNetBufferListsCompleteHandler:FFFFF8047CFAB520.
FILE:ProtocolDriver.cpp, LINE:53, OidRequestCompleteHandler:FFFFF8047CFA6DC0.
FILE:ProtocolDriver.cpp, LINE:55, DirectOidRequestCompleteHandler:FFFFF8047CFA6DC0.

FILE:ProtocolDriver.cpp, LINE:10, Name:TCPIP6TUNNEL.
FILE:ProtocolDriver.cpp, LINE:11, BindDeviceName:(null).
FILE:ProtocolDriver.cpp, LINE:12, RootDeviceName:(null).
FILE:ProtocolDriver.cpp, LINE:13, ImageName:(null).
FILE:ProtocolDriver.cpp, LINE:15, BindAdapterHandlerEx:FFFFF8047CFBFF70.
FILE:ProtocolDriver.cpp, LINE:16, UnbindAdapterHandlerEx:FFFFF8047CFAE5D0.
FILE:ProtocolDriver.cpp, LINE:17, OpenAdapterCompleteHandlerEx:FFFFF8047D0D1D30.
FILE:ProtocolDriver.cpp, LINE:18, CloseAdapterCompleteHandlerEx:FFFFF8047CFB0420.
FILE:ProtocolDriver.cpp, LINE:20, PnPEventHandler/NetPnPEventHandler:FFFFF8047CFE2E60.
FILE:ProtocolDriver.cpp, LINE:23, UninstallHandler:0000000000000000.
FILE:ProtocolDriver.cpp, LINE:26, StatusHandler/StatusHandlerEx:FFFFF8047CFC1FE0.
FILE:ProtocolDriver.cpp, LINE:29, ReceiveNetBufferListsHandler:FFFFF8047CF96D80.
FILE:ProtocolDriver.cpp, LINE:30, SendNetBufferListsCompleteHandler:FFFFF8047CF986D0.
FILE:ProtocolDriver.cpp, LINE:53, OidRequestCompleteHandler:FFFFF8047CFA6DC0.
FILE:ProtocolDriver.cpp, LINE:55, DirectOidRequestCompleteHandler:FFFFF8047CFA6DC0.

FILE:ProtocolDriver.cpp, LINE:10, Name:TCPIPTUNNEL.
FILE:ProtocolDriver.cpp, LINE:11, BindDeviceName:(null).
FILE:ProtocolDriver.cpp, LINE:12, RootDeviceName:(null).
FILE:ProtocolDriver.cpp, LINE:13, ImageName:(null).
FILE:ProtocolDriver.cpp, LINE:15, BindAdapterHandlerEx:FFFFF8047CFBFF70.
FILE:ProtocolDriver.cpp, LINE:16, UnbindAdapterHandlerEx:FFFFF8047CFAE5D0.
FILE:ProtocolDriver.cpp, LINE:17, OpenAdapterCompleteHandlerEx:FFFFF8047D0D1D30.
FILE:ProtocolDriver.cpp, LINE:18, CloseAdapterCompleteHandlerEx:FFFFF8047CFB0420.
FILE:ProtocolDriver.cpp, LINE:20, PnPEventHandler/NetPnPEventHandler:FFFFF8047CFE2E90.
FILE:ProtocolDriver.cpp, LINE:23, UninstallHandler:0000000000000000.
FILE:ProtocolDriver.cpp, LINE:26, StatusHandler/StatusHandlerEx:FFFFF8047CFC1FE0.
FILE:ProtocolDriver.cpp, LINE:29, ReceiveNetBufferListsHandler:FFFFF8047CF96D80.
FILE:ProtocolDriver.cpp, LINE:30, SendNetBufferListsCompleteHandler:FFFFF8047CF986D0.
FILE:ProtocolDriver.cpp, LINE:53, OidRequestCompleteHandler:FFFFF8047CFA6DC0.
FILE:ProtocolDriver.cpp, LINE:55, DirectOidRequestCompleteHandler:FFFFF8047CFA6DC0.

FILE:ProtocolDriver.cpp, LINE:10, Name:TCPIP6.
FILE:ProtocolDriver.cpp, LINE:11, BindDeviceName:(null).
FILE:ProtocolDriver.cpp, LINE:12, RootDeviceName:\DEVICE\{369292E4-DD92-46B9-B680-A71531F1B46E}.
FILE:ProtocolDriver.cpp, LINE:13, ImageName:tcpip.sys.
FILE:ProtocolDriver.cpp, LINE:15, BindAdapterHandlerEx:FFFFF8047CFBFF70.
FILE:ProtocolDriver.cpp, LINE:16, UnbindAdapterHandlerEx:FFFFF8047CFAE5D0.
FILE:ProtocolDriver.cpp, LINE:17, OpenAdapterCompleteHandlerEx:FFFFF8047D0D1D30.
FILE:ProtocolDriver.cpp, LINE:18, CloseAdapterCompleteHandlerEx:FFFFF8047CFB0420.
FILE:ProtocolDriver.cpp, LINE:20, PnPEventHandler/NetPnPEventHandler:FFFFF8047CFC1BF0.
FILE:ProtocolDriver.cpp, LINE:23, UninstallHandler:0000000000000000.
FILE:ProtocolDriver.cpp, LINE:26, StatusHandler/StatusHandlerEx:FFFFF8047CFC1FE0.
FILE:ProtocolDriver.cpp, LINE:29, ReceiveNetBufferListsHandler:FFFFF8047CF96D80.
FILE:ProtocolDriver.cpp, LINE:30, SendNetBufferListsCompleteHandler:FFFFF8047CF986D0.
FILE:ProtocolDriver.cpp, LINE:53, OidRequestCompleteHandler:FFFFF8047CFA6DC0.
FILE:ProtocolDriver.cpp, LINE:55, DirectOidRequestCompleteHandler:FFFFF8047CFA6DC0.

FILE:ProtocolDriver.cpp, LINE:10, Name:TCPIP.
FILE:ProtocolDriver.cpp, LINE:11, BindDeviceName:(null).
FILE:ProtocolDriver.cpp, LINE:12, RootDeviceName:\DEVICE\{369292E4-DD92-46B9-B680-A71531F1B46E}.
FILE:ProtocolDriver.cpp, LINE:13, ImageName:tcpip.sys.
FILE:ProtocolDriver.cpp, LINE:15, BindAdapterHandlerEx:FFFFF8047CFBFF70.
FILE:ProtocolDriver.cpp, LINE:16, UnbindAdapterHandlerEx:FFFFF8047CFAE5D0.
FILE:ProtocolDriver.cpp, LINE:17, OpenAdapterCompleteHandlerEx:FFFFF8047D0D1D30.
FILE:ProtocolDriver.cpp, LINE:18, CloseAdapterCompleteHandlerEx:FFFFF8047CFB0420.
FILE:ProtocolDriver.cpp, LINE:20, PnPEventHandler/NetPnPEventHandler:FFFFF8047CFC1C20.
FILE:ProtocolDriver.cpp, LINE:23, UninstallHandler:0000000000000000.
FILE:ProtocolDriver.cpp, LINE:26, StatusHandler/StatusHandlerEx:FFFFF8047CFC1FE0.
FILE:ProtocolDriver.cpp, LINE:29, ReceiveNetBufferListsHandler:FFFFF8047CF96D80.
FILE:ProtocolDriver.cpp, LINE:30, SendNetBufferListsCompleteHandler:FFFFF8047CF986D0.
FILE:ProtocolDriver.cpp, LINE:53, OidRequestCompleteHandler:FFFFF8047CFA6DC0.
FILE:ProtocolDriver.cpp, LINE:55, DirectOidRequestCompleteHandler:FFFFF8047CFA6DC0.
```

## 作者信息

made by correy  
made at 2024-01-08  
[https://github.com/kouzhudong](https://github.com/kouzhudong)
