import argparse, json
from pathlib import Path
import numpy as np
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def model(x, a1, c1, s1, a2, c2, s2, b0, b1):
    return b0+b1*(x-550)+a1*np.exp(-0.5*((x-c1)/s1)**2)+a2*np.exp(-0.5*((x-c2)/s2)**2)

def fit_spectrum(x, y):
    x,y=np.asarray(x,float),np.asarray(y,float)
    if x.ndim!=1 or x.shape!=y.shape or x.size<30 or not np.all(np.isfinite([x,y])) or np.any(np.diff(x)<=0):
        raise ValueError('Require at least 30 finite samples on an increasing wavelength axis.')
    if x[0]>535 or x[-1]<570 or np.ptp(y)<1e-8:
        raise ValueError('Require coverage 535–570 nm and nonconstant intensity.')
    p,_=curve_fit(model,x,y,p0=[1,548,3,.7,555,4,.1,0],bounds=([0,540,.3,0,552,.3,-np.inf,-np.inf],[np.inf,551,8,np.inf,563,8,np.inf,np.inf]),maxfev=20000)
    return p

def run(out,seed=42):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    x=np.linspace(530,575,451); truth=np.array([1,548,3,.7,555,4,.12,.001])
    y=model(x,*truth)+np.random.default_rng(seed).normal(0,.015,x.size)
    p=fit_spectrum(x,y); fitted=model(x,*p)
    metrics={'seed':seed,'data':'synthetic','centres_nm':p[[1,4]].tolist(),'centre_absolute_error_nm':np.abs(p[[1,4]]-truth[[1,4]]).tolist(),'fwhm_nm':(2*np.sqrt(2*np.log(2))*p[[2,5]]).tolist(),'peak_areas_au_nm':(np.sqrt(2*np.pi)*p[[0,3]]*p[[2,5]]).tolist(),'residual_rmse':float(np.sqrt(np.mean((y-fitted)**2)))}
    np.savetxt(out/'spectrum.csv',np.column_stack([x,y,fitted]),delimiter=',',header='wavelength_nm,intensity_au,fit_au',comments='')
    fig,ax=plt.subplots(2,1,figsize=(9,6),sharex=True,gridspec_kw={'height_ratios':[3,1]})
    ax[0].plot(x,y,'.',ms=2,label='Synthetic observations');ax[0].plot(x,fitted,label='Joint fit');ax[0].set_ylabel('Intensity (a.u.)');ax[0].legend();ax[0].set_title('Two overlapping spectral lines')
    ax[1].plot(x,y-fitted);ax[1].axhline(0,color='k',lw=.5);ax[1].set(xlabel='Wavelength (nm)',ylabel='Residual')
    fig.tight_layout();fig.savefig(out/'preview.png',dpi=160,bbox_inches='tight');plt.close(fig)
    (out/'metrics.json').write_text(json.dumps(metrics,indent=2));return metrics

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='results');p.add_argument('--seed',type=int,default=42);a=p.parse_args();print(json.dumps(run(a.out,a.seed),indent=2))

