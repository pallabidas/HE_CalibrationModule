import numpy
import ROOT
from ROOT import TCanvas
from ROOT import TFile
from ROOT import TH1F
from ROOT import TF1
from ROOT import TGraph
from ROOT import TPaveText
from array import array
from HttStyles import GetStyleHtt
from HttStyles import MakeCanvas


class ADCConverter:
    # Bitmasks for 8-bit ADC input
    expMask = 192
    manMask = 63

    baseSensitivity = 3.1

    # Base charges for each subrange
    # Use array for which 0 ADC = 0 fC input charge
    inputCharge = [
        -1.6, 48.4, 172.4, 433.4, 606.4,
        517, 915, 1910, 3990, 5380,
        4780, 7960, 15900, 32600, 43700,
        38900, 64300, 128000, 261000, 350000
    ]

    #Defines the size of the ADC mantissa subranges
    adcBase = [0, 16, 36, 57, 64]

    # A class to convert ADC to fC
    fc = {}

    def __init__(self):
        # Loop over exponents, 0 - 3
        for exp in xrange(0, 4):
            # Loop over mantissas, 0 - 63
            for man in xrange(0, 64):
                subrange = -1

                # Find which subrange the mantissa is in
                for i in xrange(0, 4):
                    if man >= self.adcBase[i] and man < self.adcBase[i + 1]:
                        subrange = i
                if subrange == -1:
                    print "Something has gone horribly wrong!"

                # Sensitivity = 3.1 * 8^exp * 2^subrange
                sensitivity = self.baseSensitivity * 8.0**float(exp) * 2.0**subrange

                # Add sensitivity * (location in subrange) to base charge
                #fc[exp * 64 + man] = (inputCharge[exp * 5 + subrange] + ((man - adcBase[subrange])) * sensitivity) / gain;
                self.fc[exp * 64 + man] = self.inputCharge[exp * 5 + subrange] + ((man - self.adcBase[subrange]) + .5) * sensitivity

    def linearize(self, adc):
        return self.fc[adc]


adc2fC = ADCConverter()

def getData(f):
    link = 0
    iBin = 0
    event = 0
    valid = False
    totalValid = False
    totalData = []
    dataArray = {}
    tempDataArray = []
    for line in f:
        if "START EVENT" in line:
            if dataArray != {} and totalValid:
                totalData.append(dataArray)
            event = int(line.split()[3].strip("-"))
            totalValid = True
            dataArray = {}
        if "N  RAW0  RAW1" in line or "START EVENT" in line:
            if valid and tempDataArray !=[]:
                dataArray[int(link)] = tempDataArray
            if "N  RAW0  RAW1" in line: link = int(line.split(":")[1])
            iBin = 0
            valid = True
            tempDataArray = []
        if "(Suspicious data format!)" in line:
            valid = False
            totalValid = False
        if "ADC:" in line:
            data = line.split(":")[1]
            datums = data.split()
            linDatum = []
            for datum in datums:
                linDatum.append(adc2fC.linearize(int(datum)))
            tempDataArray.append(linDatum)
            iBin += 1
    return totalData

    #means = {}
    #sumws = {}
    #for event in totalData:
    #    for link in event:
    #        iChan = (link - 15)*6
    #        for chan in xrange(0, 6):
    #            #ped = 0
    #            #for iBin in xrange(20, 50):
    #            #    ped += event[link][iBin][chan]
    #            #ped /= 30.0
    #
    #            if not iChan in means:
    #                means[iChan] = []
    #                sumws[iChan] = 0
    #            for iBin in xrange(0, 99):
    #                #means[iChan] += event[link][iBin][chan] - ped
    #                means[iChan].append(event[link][iBin][chan])
    #            sumws[iChan] += 1.0
    #            iChan += 1
    #
    ##for i in means:
    ##    means[i] /= sumws[i]
    #rmeans = {}
    #for iChan in means:
    #    rmeans[iChan] = numpy.std(means[iChan])
    #return rmeans

def getTDCValues(f):
    link = 0
    iBin = 0
    event = 0
    valid = False
    totalValid = False
    totalData = []
    dataArray = {}
    tempDataArray = []
    for line in f:
        if "START EVENT" in line:
            if dataArray != {}:
                totalData.append(dataArray)
            event = int(line.split()[3].strip("-"))
            totalValid = True
            dataArray = {}
        if "N  RAW0  RAW1" in line:
            if valid:
                dataArray[int(link)] = tempDataArray
            link = int(line.split(":")[1])
            iBin = 0
            valid = True
            tempDataArray = []
        if "(Suspicious data format!)" in line:
            valid = False
            totalValid = False
        if "TDC:" in line:
            data = line.split(":")[1]
            datums = data.split()
            linDatum = []
            for datum in datums:
                linDatum.append(int(datum)/2.0)
            tempDataArray.append(linDatum)
            iBin += 1

    return totalData






def Measure_Integral(Fname1,Fname2,Title, XaxisT,low,high,freq,RootName):

    FNumber=int((high-low)/freq)
    
    LINK=[19]
    #    LINK=[15,16,17,18,19]
    #    LINKkChannel=[0,1,2,3,4,5]
    LINKkChannel=[2]
    for linkChannel in LINKkChannel:
        for link in LINK:
            xIntegral=array("d",xrange(0,FNumber))
            yIntegral=array("d",xrange(0,FNumber))
            yIntegralErrUp=array("d",xrange(0,FNumber))
            yIntegralErrDown=array("d",xrange(0,FNumber))
            xIntegral_RMS=array("d",xrange(0,FNumber))
            yIntegral_RMS=array("d",xrange(0,FNumber))
            yIntegral_RMSErrUp=array("d",xrange(0,FNumber))
            yIntegral_RMSErrDown=array("d",xrange(0,FNumber))
            xRatio=array("d",xrange(0,FNumber))
            yRatio=array("d",xrange(0,FNumber))
            xSingleEv=array("d",xrange(0,40))
            ySingleEv=array("d",xrange(0,40))
            num=-1
            for iAmp in range(low,high,freq):
                num+=1
                Fname=Fname1+str(iAmp)+Fname2
                print "*************  -> initiating      The ", Fname , " and number of files exist= ", FNumber
                print "-------------------->  Now is doing ....  ", low, "  ____ ", Fname
                
                
                f = open(Fname)
                data = getData(f)
#                tdc = getTDCValues(f)

                M=TH1F(Fname,Fname,2000,0,1000000)
                x = array("d", xrange(0,1001))
                y = array("d", xrange(0,1001))
                
                
                for event in xrange(0,995):
    
    
    
                    pedSum=0
                    sigSum=0
                    Signal=0
                    Pedestal=0
                    for BX in xrange(0, 40):

                        adcValue=data[event][link][BX][linkChannel]
                        if BX < 15 : pedSum += adcValue
                        if BX > 19 and  BX < 25: sigSum += adcValue
                        xSingleEv[BX]=BX
                        ySingleEv[BX]=adcValue
                
                    scanvas = MakeCanvas("mm","nn",800,800)
                    GrSingleEv=TGraph(len(xSingleEv),xSingleEv,ySingleEv)
                    SFit=TF1("fit", "gaus", 19,23)
                    SFit.SetParameter(0, 4000)
                    SFit.SetParameter(1, 20.9)
                    SFit.SetParLimits(1, 20, 22)
                    SFit.SetParameter(2, 1.5)
                    GrSingleEv.Draw("AC*")
                    GrSingleEv.Fit("fit","R0")
                    SFit.Draw("same")
                    FitParam=SFit.GetParameters()
                    print "Gaus fit param 1, 2, 3= " , round(FitParam[0],4), round(FitParam[1],4), round(FitParam[2],4)
        #            scanvas.SaveAs("singleEv_"+str(iAmp)+"_"+str(event)+".pdf")

                    Pedestal=pedSum/15.
                    y[event]= sigSum- Pedestal*5
                    M.Fill(y[event])

                histMean= M.GetMean()
                histRMS= M.GetStdDev()

                highVal = histMean + 4 * histRMS
                lowVal = histMean - 4 * histRMS
                highValAx = histMean + 6 * histRMS
                lowValAx = histMean - 6 * histRMS

                canvas = MakeCanvas("asdf","asdf",800,800)
                canvas.Update()
                MyGr= TGraph(len(x), x,y)
                mfit=TF1("fit", "gaus", lowVal,highVal)
                M.Fit(mfit, "R0","")
                FitParam=mfit.GetParameters()
        #        FitParErr=mfit.GetParError()
                integral= round(FitParam[1],4)
                integral_RMS= round(FitParam[2],4)
                integralErr= round(mfit.GetParError(1),4)
                integral_RMSErr= round(mfit.GetParError(2),4)
                print "iAmp=", iAmp, "   integral= ", integral,  "   integral_RMS=", integral_RMS


                M.SetMarkerStyle(22)
                M.GetXaxis().SetRangeUser(lowValAx,highValAx)
                
                M.SetTitle(Title+" = "+str(iAmp))
                M.Draw("pe")
                mfit.Draw("same")
                fitInfo  =TPaveText(.20,0.7,.60,0.9, "NDC");
                fitInfo.SetBorderSize(   0 );
                fitInfo.SetFillStyle(    0 );
                fitInfo.SetTextAlign(   12 );
                fitInfo.SetTextSize ( 0.03 );
                fitInfo.SetTextColor(    1 );
                fitInfo.SetTextFont (   62 );
                fitInfo.AddText("Mean of Fit=" + str(round(FitParam[1],1)))
                fitInfo.AddText("RMS of Fit =" + str(round(FitParam[2],1)))
                fitInfo.Draw()
                canvas.SaveAs("HistoSingleRun_"+str(iAmp)+"_"+Title+RootName+"_link"+str(link)+"_ch_"+str(linkChannel)+".pdf")



                xIntegral[num]=iAmp
                yIntegral[num]=integral
                yIntegralErrUp[num]=integral+integralErr
                yIntegralErrDown[num]=integral-integralErr

                xIntegral_RMS[num]=iAmp
                yIntegral_RMS[num]=integral_RMS
                yIntegral_RMSErrUp[num]=integral_RMS+integral_RMSErr
                yIntegral_RMSErrDown[num]=integral_RMS-integral_RMSErr
                
                xRatio[num]=iAmp
                yRatio[num]=integral_RMS/integral



            Graph_Integral= TGraph(len(xIntegral), xIntegral,yIntegral)
            Graph_IntegralErUp= TGraph(len(xIntegral), xIntegral,yIntegralErrUp)
            Graph_IntegralErDown= TGraph(len(xIntegral), xIntegral,yIntegralErrDown)
            
            canvas_Integral = MakeCanvas("can1","can1",800,800)
            Graph_Integral.SetTitle("Pulse Integral vs. Pulse  "+Title)
            Graph_Integral.SetMarkerStyle(22)
            Graph_Integral.SetMarkerColor(3)
            Graph_Integral.SetMarkerSize(2)
            Graph_Integral.GetXaxis().SetTitle(XaxisT)
            Graph_Integral.Draw()
            Graph_IntegralErUp.Draw("same")
            Graph_IntegralErDown.Draw("same")
            canvas_Integral.SaveAs("Integral_"+Title+RootName+"_link"+str(link)+"_ch_"+str(linkChannel)+".pdf")

            Graph_Integral_RMS= TGraph(len(xIntegral_RMS), xIntegral_RMS,yIntegral_RMS)
            Graph_Integral_RMSErUp= TGraph(len(xIntegral_RMS), xIntegral_RMS,yIntegral_RMSErrUp)
            Graph_Integral_RMSErDown= TGraph(len(xIntegral_RMS), xIntegral_RMS,yIntegral_RMSErrDown)

            canvas_Integral_RMS = MakeCanvas("can2","can2",800,800)
            Graph_Integral_RMS.SetTitle("Pulse Integral RMS vs. Pulse  "+Title)
            Graph_Integral_RMS.SetMarkerStyle(23)
            Graph_Integral_RMS.SetMarkerColor(2)
            Graph_Integral_RMS.SetMarkerSize(2)
            Graph_Integral_RMS.GetXaxis().SetTitle(XaxisT)
            Graph_Integral_RMS.Draw()
            Graph_Integral_RMSErUp.Draw("same")
            Graph_Integral_RMSErDown.Draw("same")
            canvas_Integral_RMS.SaveAs("Integral_RMS_"+Title+RootName+"_link"+str(link)+"_ch_"+str(linkChannel)+".pdf")


            Graph_Ratio= TGraph(len(xRatio), xRatio,yRatio)
            canvas_Ratio = MakeCanvas("can2","can2",800,800)
            Graph_Ratio.SetTitle("Ratio of Pulse Integral RMS and Pulse Integral  "+Title)
            Graph_Ratio.SetMarkerStyle(21)
            Graph_Ratio.SetMarkerColor(8)
            Graph_Ratio.SetMarkerSize(2)
            Graph_Ratio.GetXaxis().SetTitle(XaxisT)
            Graph_Ratio.Draw()
            canvas_Ratio.SaveAs("Ratio_"+Title+RootName+"_link"+str(link)+"_ch_"+str(linkChannel)+".pdf")

            OutFile=TFile("outFile_"+RootName+"_link"+str(link)+"_ch_"+str(linkChannel)+".root","RECREATE")
            OutFile.WriteObject(Graph_Integral,"Graph_Integral")
            OutFile.WriteObject(Graph_Integral_RMS,"Graph_Integral_RMS")
            OutFile.WriteObject(Graph_Ratio,"Graph_Ratio")
            OutFile.Close()



####################################################################################################################################
#       Amplitude v.s. pulse amplitude setting
####################################################################################################################################

Do_Charge_vs_Amplitude=1
###
if Do_Charge_vs_Amplitude:
    Title="Height"
    XaxisT="height * 0.1"
    low=3
    high=11
    freq=1


    Fname1="_FRI_Feb26_AMP_Var/FRI_Feb26_Delay3_WID4_AMP"
    Fname2=".txt"
    RootName="_PulseIntegral_Delay3_WID4_AMP"
    Measure_Integral(Fname1,Fname2, Title, XaxisT,low,high,freq,RootName)

    Fname1="_FRI_Feb26_AMP_Var/FRI_Feb26_Delay3_WID10_AMP"
    Fname2=".txt"
    RootName="_PulseIntegral_Delay3_WID10_AMP"
    Measure_Integral(Fname1,Fname2, Title, XaxisT,low,high,freq,RootName)


    Fname1="_FRI_Feb26_AMP_Var/FRI_Feb26_Delay3_WID22_AMP"
    Fname2=".txt"
    RootName="_PulseIntegral_Delay3_WID22_AMP"
    Measure_Integral(Fname1,Fname2, Title, XaxisT,low,high,freq,RootName)


####################################################################################################################################
#       Amplitude v.s. pulse width setting
####################################################################################################################################
Do_Charge_vs_Width=0
###
if Do_Charge_vs_Width:
    Title="Width"
    XaxisT="Width"
    low=4
    high=24
    freq=2

#    Fname1="BigFRIDAY/Friday_WID_AMP0p1/Fri_AMP0p1_WID"
#    Fname2=".txt"
#    RootName="fc_vs_width_AMP1.root"
#    Measure_Integral(Fname1,Fname2, Title, XaxisT,low,high,freq,RootName)

    Fname1="_FRI_Feb26_WID_Var/FRI_Feb26_Delay3_AMP5_WID"
    Fname2=".txt"
    RootName="_PulseIntegral_Delay3_AMP5_WID"
    Measure_Integral(Fname1,Fname2, Title, XaxisT,low,high,freq,RootName)


    Fname1="_FRI_Feb26_WID_Var/FRI_Feb26_Delay3_AMP9_WID"
    Fname2=".txt"
    RootName="_PulseIntegral_Delay3_AMP5_WID"
    Measure_Integral(Fname1,Fname2, Title, XaxisT,low,high,freq,RootName)


















    
    
