#include "EthernetScannerSDKDefine.h"

#if !defined(ETHERNETSCANNERHEADER)
#define ETHERNETSCANNERHEADER

#if !defined (_MSC_VER)
#define _stdcall
#endif

#ifdef __cplusplus
extern "C" {
#endif  /* __cplusplus */

//DLL-Functions

/*
*/
extern void* _stdcall EthernetScanner_Connect(char *chIP, char *chPort, int uiTimeOut);

/*
*/
extern void _stdcall EthernetScanner_ConnectEx(void* vHandle, char *chIP, char *chPort, int uiTimeOut);

/*
*/
extern void* _stdcall EthernetScanner_Disconnect(void *pEthernetScanner);

/*
*/
extern void _stdcall EthernetScanner_GetConnectStatus(void *pEthernetScanner, int *iConnectStatus);

/*
*/
extern int _stdcall EthernetScanner_GetXZIExtended(void *pEthernetScanner, double *pdoX, double *pdoZ, int *piIntensity, int *piPeakWidth, int iBuffer, unsigned int *puiEncoder, unsigned char *pucUSRIO, int dwTimeOut, unsigned char *ucBufferRaw, int iBufferRaw, int *iPicCnt);

/*
*/
extern int _stdcall EthernetScanner_GetInfo(void *pEthernetScanner, char *chInfo, int iBuffer, char *chMode);

/*
*/
extern int _stdcall EthernetScanner_GetDllFiFoState(void *pEthernetScanner);

/*
*/
extern int _stdcall EthernetScanner_ResetDllFiFo(void *pEthernetScanner);

/*
*/
extern int _stdcall EthernetScanner_WriteData(void *pEthernetScanner, char *cBuffer, int uiBuffer);

/*
*/
extern int _stdcall EthernetScanner_ReadData(void* pEthernetScanner, char * chPropertyName, char * chRetBuf, int iRetBuf, int iCashTime);


/*
*/
extern int _stdcall EthernetScanner_GetVersion(unsigned char *ucBuffer, int uiBuffer);


/*
*/
extern int _stdcall EthernetScanner_GetImage(void* pEthernetScanner, char *cBuffer, int iBuffer, unsigned int *puiWidth, unsigned int *puiHeight, unsigned int *puiOffsetX, unsigned int *puiOffsetZ, unsigned int *puiStepX, unsigned int *puiStepZ, unsigned int iTimeOut);

/*
*/
extern void _stdcall EthernetScanner_SetReadDataCallback(void* obj, void* callback);

/*
*/
extern int _stdcall EthernetScanner_ConvertMmToPix(void* pEthernetScanner, double RoiMmL, double RoiMmT, double RoiMmR, double RoiMmB, int * RoiPixL, int * RoiPixT, int * RoiPixR, int * RoiPixB);
  
/*
*/
extern void* _stdcall EthernetScanner_ConnectUDP(char* chDestIP, char* chDestPort, char* chSrcIP, char* chSrcPort, char* chMode);

 /*
 */
extern int _stdcall EthernetScanner_GetRangeImage(void* pEthernetScanner, unsigned short* imageBuffer, int iBuffer, int iTimeOutPerScan, bool* bFrameLost=nullptr , int* picCntBuffer=nullptr, int* encoderBuffer=nullptr, unsigned int* timeStampBuffer = nullptr);



#ifdef __cplusplus
};
#endif  /* __cplusplus */

#endif
