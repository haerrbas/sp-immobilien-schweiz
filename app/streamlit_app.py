"""
streamlit_app.py — Interaktive Web App Swiss Real Estate Prices
Starten: streamlit run app/streamlit_app.py
"""
import sys; sys.path.insert(0, '.')
import streamlit as st, pandas as pd, numpy as np
import matplotlib.pyplot as plt, seaborn as sns
import scipy.stats as stats
from pathlib import Path
from itertools import combinations

st.set_page_config(page_title="Swiss Real Estate Prices", page_icon="home", layout="wide")

@st.cache_data
def lade_daten():
    p = Path("data/inserate_bereinigt.csv")
    if p.exists(): return pd.read_csv(p)
    from src.scraper import ImmobilienScraper
    df = pd.DataFrame([i.to_dict() for i in ImmobilienScraper().generiere_beispieldaten(40)])
    df['preiskategorie'] = pd.cut(df['preis_chf'], bins=[0,1200,2200,99999], labels=['guenstig','mittel','teuer'])
    df['zimmer_gruppe'] = pd.cut(df['zimmer_anzahl'], bins=[0,1.5,2.5,3.5,99], labels=['1-1.5 Zi','2-2.5 Zi','3-3.5 Zi','4+ Zi'])
    return df

df = lade_daten()
st.title("Swiss Real Estate Prices")
st.markdown("Interactive analysis of rental apartment listings - SP Project FS2026")
st.divider()

with st.sidebar:
    st.header("Filter")
    staedte_all = sorted(df['stadt'].dropna().unique())
    staedte_sel = st.multiselect("Cities", staedte_all, default=staedte_all)
    p_min, p_max = st.slider("Price (CHF/mo.)", int(df['preis_chf'].min()), int(df['preis_chf'].max()),
        (int(df['preis_chf'].quantile(0.05)), int(df['preis_chf'].quantile(0.95))))
    z_min, z_max = st.slider("Rooms", float(df['zimmer_anzahl'].min()), float(df['zimmer_anzahl'].max()), (1.0,5.0), step=0.5)

dff = df[df['stadt'].isin(staedte_sel) & df['preis_chf'].between(p_min,p_max) & df['zimmer_anzahl'].between(z_min,z_max)]

c1,c2,c3,c4 = st.columns(4)
c1.metric("Listings", f"{len(dff):,}")
c2.metric("Price (avg)", f"CHF {dff['preis_chf'].mean():,.0f}" if len(dff) else "n/a")
c3.metric("Area (avg)", f"{dff['flaeche_m2'].mean():.0f} m2" if len(dff) else "n/a")
c4.metric("Cities", f"{dff['stadt'].nunique()}")
st.divider()

tab1,tab2,tab3,tab4 = st.tabs(["Overview","Analysis","Data","Statistics"])

with tab1:
    col1,col2 = st.columns(2)
    with col1:
        st.subheader("Price Distribution by City")
        if len(dff) > 0:
            fig,ax = plt.subplots(figsize=(7,4))
            order = dff.groupby('stadt')['preis_chf'].median().sort_values(ascending=False).index
            sns.boxplot(data=dff, y='stadt', x='preis_chf', order=order, palette='husl', ax=ax)
            ax.set_xlabel("CHF/month"); ax.set_ylabel("")
            plt.tight_layout(); st.pyplot(fig)
    with col2:
        st.subheader("Price/m2 by City")
        if len(dff) > 0:
            fig,ax = plt.subplots(figsize=(7,4))
            pm2 = dff.groupby('stadt')['preis_pro_m2'].mean().sort_values()
            ax.barh(pm2.index, pm2.values, color=sns.color_palette('husl',len(pm2)))
            ax.set_xlabel("CHF/m2")
            plt.tight_layout(); st.pyplot(fig)

with tab2:
    col1,col2 = st.columns(2)
    with col1:
        st.subheader("Area vs. Rental Price")
        if len(dff) > 5:
            fig,ax = plt.subplots(figsize=(7,5))
            for s in dff['stadt'].unique():
                sub = dff[dff['stadt']==s]
                ax.scatter(sub['flaeche_m2'],sub['preis_chf'],alpha=0.5,s=25,label=s)
            x,y = dff['flaeche_m2'].values, dff['preis_chf'].values
            m,b,r,p,_ = stats.linregress(x,y)
            xl = np.linspace(x.min(),x.max(),100)
            ax.plot(xl,m*xl+b,'k--',lw=2,label=f'R2={r**2:.3f}')
            ax.legend(fontsize=8,ncol=2); ax.set_xlabel("m2"); ax.set_ylabel("CHF")
            plt.tight_layout(); st.pyplot(fig)
    with col2:
        st.subheader("Price by Room Group")
        if len(dff) > 0:
            fig,ax = plt.subplots(figsize=(7,5))
            zo = [z for z in ['1-1.5 Zi','2-2.5 Zi','3-3.5 Zi','4+ Zi'] if z in dff['zimmer_gruppe'].values]
            sns.violinplot(data=dff,x='zimmer_gruppe',y='preis_chf',order=zo,palette='muted',ax=ax,inner='quartile')
            plt.tight_layout(); st.pyplot(fig)

with tab3:
    st.subheader("Summary Table")
    if len(dff) > 0:
        t = dff.groupby('stadt').agg(n=('preis_chf','count'),preis=('preis_chf','mean'),
            median=('preis_chf','median'),flaeche=('flaeche_m2','mean'),
            zimmer=('zimmer_anzahl','mean'),m2=('preis_pro_m2','mean')).round(1)
        t.columns=['n','Preis (CHF)','Median','Area (m2)','Rooms','CHF/m2']
        st.dataframe(t.sort_values('Preis (CHF)',ascending=False),use_container_width=True)
    st.subheader("Raw Data")
    st.dataframe(dff.head(100),use_container_width=True)

with tab4:
    st.subheader("Correlation Analysis (Pearson r + p-value)")
    num_cols = ['preis_chf','flaeche_m2','zimmer_anzahl','preis_pro_m2']
    dn = dff[num_cols].dropna()
    if len(dn) > 5:
        fig,ax = plt.subplots(figsize=(6,5))
        sns.heatmap(dn.corr(),annot=True,fmt='.3f',cmap='RdYlGn',vmin=-1,vmax=1,center=0,
                    mask=np.triu(np.ones_like(dn.corr(),dtype=bool)),square=True,ax=ax)
        ax.set_title("Pearson-Korrelationsmatrix"); plt.tight_layout(); st.pyplot(fig)
        rows = [{'V1':c1,'V2':c2,'r':round(r,4),'p':round(p,6),
                 'sig':'***' if p<0.001 else '**' if p<0.01 else '*' if p<0.05 else 'n.s.'}
                for c1,c2 in combinations(num_cols,2) for r,p in [stats.pearsonr(dn[c1],dn[c2])]]
        st.dataframe(pd.DataFrame(rows),use_container_width=True)
