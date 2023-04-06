import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from information import *

def draw_globalmap(da,grid,crsP=ccrs.Robinson(central_longitude=-90),cname=None):
    if 'basin' in grid.data_vars:
        landmask = generate_masks(grid)['global']
        geolon = 'geolon'
        geolat = 'geolat'
    else:
        landmask = grid['mask']
        geolon = 'GEOLON'
        geolat = 'GEOLAT'
    
    crsT = ccrs.PlateCarree()

    fig,ax = plt.subplots(figsize=(10,10),subplot_kw={'projection':crsP})

    X = grid[geolon]
    Y = grid[geolat]
    Z = da.where(landmask)

    im = ax.pcolormesh(X,Y,Z,transform=crsT,shading='auto')

    ax.gridlines(color='gray',linestyle='dashed')
    ax.add_feature(cfeature.LAND,color='lightgrey')
    ax.set_title(da.name,fontsize=14)

    # Finally, add a colorbar
    cbar = plt.colorbar(im,ax=ax,orientation='horizontal',fraction=0.03,pad=0.05)
    if cname is not None:
        cbar.set_label(cname,fontsize=12)
    
    fig.tight_layout()
    
    return fig,ax,im,cbar

def draw_ppp_regionalmeans(ds,colors=None):
    threshold = 0.235559205
    fig,ax=plt.subplots(figsize=(12,4))
    lines = []
    for i,(name,da) in enumerate(ds.items()):
        line, = ax.plot(da['time']+1,da,label=name)
        lines.append(line);
        if colors is not None:
            lines[i].set_color(colors[name])
    ax.legend(frameon=False)
    ax.set_xlabel('Time (months)')
    ax.set_ylabel('Potential Prognostic Predictability')
    ax.set_xlim([0,da['time'].max()])
    ax.set_ylim([0,1])
    ax.axhline(threshold,linestyle='--',color='gray')
    return fig,ax,lines

def save_fig(fig,figname,variable,filename,addnames=None):
    savedir = ppeDict['figsavedir']+'/'+figname+'/'
    savenames = [figname,variable,filename]
    if addnames is not None:
        for addname in addnames:
            savenames.append(addname)
    savename = '.'.join(savenames)
    fig.savefig(savedir+savename+'.png',transparent=True,dpi=300,bbox_inches='tight')