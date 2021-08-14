import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
from adjustText import adjust_text
import os
from matplotlib.offsetbox import OffsetImage
import sys
from svgpath2mpl import parse_path
from termcolor import colored
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
from matplotlib.legend_handler import HandlerPatch

COLORS = {'ARI':'#97233F','ATL':'#A71930','BAL':'#241773','BUF':'#00338D','CAR':'#0085CA','CHI':'#00143F',
          'CIN':'#FB4F14','CLE':'#FB4F14','DAL':'#B0B7BC','DEN':'#002244','DET':'#046EB4','GB':'#24423C',
          'HOU':'#C9243F','IND':'#003D79','JAX':'#136677','KC':'#CA2430','LA':'#002147','LAC':'#2072BA',
          'LV':'#C4C9CC','MIA':'#0091A0','MIN':'#4F2E84','NE':'#0A2342','NO':'#A08A58','NYG':'#192E6C',
          'NYJ':'#203731','PHI':'#014A53','PIT':'#FFC20E','SEA':'#7AC142','SF':'#C9243F','TB':'#D40909',
          'TEN':'#4095D1','WAS':'#FFC20F'}
COLORS2 = {'ARI':'#000000','ATL':'#000000','BAL':'#000000','BUF':'#c60c30','CAR':'#000000','CHI':'#c83803',
          'CIN':'#fb4f14','CLE':'#22150c','DAL':'#b0b7bc','DEN':'#fb4f14','DET':'#b0b7bc','GB':'#ffb612',
          'HOU':'#a71930','IND':'#a5acaf','JAX':'#006778','KC':'#ffb612','LA':'#b3995d','LAC':'#0073cf',
          'LV':'#000000','MIA':'#f58220','MIN':'#ffc62f','NE':'#c60c30','NO':'#000000','NYG':'#a71930',
          'NYJ':'#1c2d25','PHI':'#a5acaf','PIT':'#ffb612','SEA':'#69be28','SF':'#b3995d','TB':'#34302b',
          'TEN':'#4b92db','WAS':'#ffb612'}

TEAMS = {'ARI':'CARDINALS','ATL':'FALCONS','BAL':'RAVENS','BUF':'BILLS','CAR':'PANTHERS','CHI':'BEARS',
          'CIN':'BENGALS','CLE':'BROWNS','DAL':'COWBOYS','DEN':'BRONCOS','DET':'LIONS','GB':'PACKERS',
          'HOU':'TEXANS','IND':'COLTS','JAX':'JAGUARS','KC':'CHIEFS','LA':'RAMS','LAC':'CHARGERS',
          'LV':'RAIDERS','MIA':'DOLPHINS','MIN':'VIKINGS','NE':'PATRIOTS','NO':'SAINTS','NYG':'GIANTS',
          'NYJ':'JETS','PHI':'EAGLES','PIT':'STEELERS','SEA':'SEAHAWKS','SF':'49ERS','TB':'BUCCANEERS',
          'TEN':'TITANS','WAS':'WASHINGTON'}

TAGS = {'ARI':'#RedSea','ATL':'#RiseUpATL','BAL':'#RavensFlock','BUF':'#BillsMafia','CAR':'#KeepPounding','CHI':'#DaBears',
          'CIN':'#SEIZETHEDEY','CLE':'#Browns','DAL':'#DallasCowboys','DEN':'#BroncosCountry','DET':'#OnePride','GB':'#GoPackGo',
          'HOU':'#WeAreTexans','IND':'#ForTheShoe','JAX':'#DUUUVAL','KC':'#ChiefsKingdom','LA':'#RamsHouse','LAC':'#BoltUp',
          'LV':'#RaiderNation','MIA':'#FinsUp','MIN':'#Skol','NE':'#GoPats','NO':'#Saints','NYG':'#TogetherBlue',
          'NYJ':'#JetsNation','PHI':'#FlyEaglesFly','PIT':'#HereWeGo','SEA':'#Seahawks','SF':'#FTTB','TB':'#GoBucs',
          'TEN':'#Titans','WAS':'#WashingtonFootball'}

ball = parse_path(""""M 95,476.91509 C 58.157481,471.21485 39.720221,459.69438 29.97449,436.28408 12.737311,394.87852 18.58815,323.63778 45.027192,253 77.017335,167.53122 131.54686,101.55515 204.88025,59.591443 243.08851,37.727457 285.88208,22.714798 331,15.34665 c 15.13467,-2.471623 18.85831,-2.696317 45,-2.715427 27.30091,-0.01996 29.04695,0.09471 41.5,2.725373 13.02787,2.752093 26.00005,7.304957 35.12421,12.327591 7.07287,3.89345 20.36247,17.574576 24.75312,25.482364 11.79401,21.241669 17.28731,54.033299 14.75912,88.103049 -2.82874,38.12007 -10.13304,69.50269 -24.83171,106.68832 -24.5663,62.14938 -65.71852,116.07671 -118.80474,155.68594 -8.5343,6.3677 -25.55908,17.75952 -31.75,21.24493 -2.0625,1.16117 -5.4375,3.06901 -7.5,4.23966 -8.41466,4.77606 -33.87044,17.19236 -41.06016,20.02748 C 216.1861,469.66262 172.9153,478.7191 126.5,478.81133 112.53275,478.83908 104.18898,478.3368 95,476.91509 Z M 215.5,451.7637 c 5.5,-1.6145 11.8,-3.42837 14,-4.03082 2.2,-0.60245 8.95,-2.97906 15,-5.28136 9.76351,-3.71546 10.97116,-4.43739 10.74344,-6.42235 -0.36186,-3.15409 -11.23302,-26.70032 -16.30715,-35.32021 C 221.45666,371.0147 207.22248,351.953 185,328.48019 161.64132,303.80725 137.9464,283.62347 113.0986,267.23319 91.802283,253.18557 66.541224,241.43801 64.05984,244.4279 61.639833,247.34383 45,296.80299 45,301.08013 c 0,0.49365 3.669066,2.74232 8.15348,4.99704 41.900936,21.06738 86.52417,61.56336 120.02396,108.92283 7.41007,10.4758 18.65491,28.66431 22.74367,36.78788 2.09444,4.16124 2.26776,4.26754 5.86854,3.59957 C 203.83034,455.00888 210,453.3782 215.5,451.7637 Z M 136.26457,240.25392 c 0.97051,-0.87465 2.99551,-3.53878 4.5,-5.92031 1.50449,-2.38152 2.99689,-4.33084 3.31645,-4.33182 1.59262,-0.005 2.97525,4.72 2.07449,7.0892 -2.04488,5.37843 3.65847,8.09503 7.96137,3.79213 2.84723,-2.84723 2.14942,-9.53414 -1.49332,-14.31002 C 151.1806,224.68129 150,222.62165 150,221.99613 c 0,-0.62553 1.885,-3.37282 4.1889,-6.1051 l 4.18889,-4.96778 2.40369,2.40369 c 2.12813,2.12813 2.25062,2.6488 1.0684,4.54183 -1.66044,2.6588 -0.19608,5.47576 3.10011,5.96361 2.9768,0.44057 7.05105,-3.46624 7.04627,-6.75669 -0.004,-2.66529 -2.83087,-8.07649 -6.05614,-11.59211 -1.81657,-1.98012 -1.7625,-2.11517 3.00279,-7.5 l 4.85267,-5.48358 2.61546,2.43676 c 1.76642,1.64573 2.28653,2.76567 1.6022,3.45 -1.70387,1.70387 -1.13039,5.48018 1.00587,6.62347 2.76785,1.48131 7.14814,-0.701 8.36773,-4.16891 1.13424,-3.22519 -0.55006,-7.81869 -4.52823,-12.34957 l -2.73662,-3.11684 5.23558,-5.8538 5.23558,-5.85379 2.23211,2.83766 c 1.52955,1.94452 1.90833,3.16143 1.20342,3.86634 -1.68892,1.68892 -1.16754,5.484 0.90585,6.59364 2.51771,1.34744 6.56644,-0.16399 8.09621,-3.02239 1.53053,-2.85982 0.49112,-7.89448 -2.55718,-12.3864 C 199.1131,169.55143 198,167.57829 198,167.17143 c 0,-0.40686 2.50235,-3.19938 5.56077,-6.20559 5.36434,-5.27276 5.61257,-5.39596 7.02706,-3.4877 1.02714,1.38568 1.27842,3.23097 0.83901,6.16118 -0.51696,3.44735 -0.30188,4.35375 1.22294,5.15369 1.01762,0.53386 2.76584,0.62417 3.88494,0.20069 5.42606,-2.05332 6.25733,-8.26009 2.06446,-15.41468 C 217.16963,151.13968 216,148.9866 216,148.79439 c 0,-0.19221 2.68263,-2.71082 5.9614,-5.59691 l 5.9614,-5.24745 1.61738,3.12768 c 1.36218,2.63416 1.4186,3.60759 0.35756,6.16917 -1.14352,2.76071 -1.0499,3.21149 1.01407,4.8828 1.85226,1.49986 2.67391,1.62827 4.43105,0.69246 5.36043,-2.8548 5.98904,-7.75668 2.01689,-15.72774 l -2.64024,-5.29828 4.39024,-3.90879 c 2.41464,-2.14983 5.61392,-4.58336 7.10951,-5.40784 2.63322,-1.45163 2.76968,-1.40155 4.31283,1.58256 1.20985,2.33959 1.31916,3.41225 0.45397,4.45474 -1.70855,2.05868 -0.77677,5.65874 1.70008,6.56852 1.57098,0.57704 2.90759,0.2355 4.75,-1.21374 3.2922,-2.58964 3.45203,-8.37412 0.40022,-14.48477 l -2.16363,-4.33226 2.66363,-2.66363 c 3.19054,-3.19054 3.48727,-7.76136 0.73624,-11.34091 -2.47733,-3.22342 -7.87825,-3.309135 -12.09448,-0.19195 l -3.05418,2.25806 -3.21197,-1.97409 C 236.41252,98.499558 230.75131,97.527542 228.05743,98.969265 225.17008,100.51453 223.7988,104.34062 225,107.5 c 1.0762,2.83063 3.53688,3.22909 6.02664,0.97589 1.56837,-1.41935 4.97336,-1.12601 4.97336,0.42846 0,0.37971 -3.02028,3.09761 -6.71173,6.03977 l -6.71173,5.3494 -2.93853,-1.68649 c -1.61619,-0.92756 -4.823,-1.94478 -7.12624,-2.26047 -3.71726,-0.50951 -4.4306,-0.26522 -6.34974,2.17458 -4.70386,5.97999 -0.37277,12.69452 5.03286,7.80249 1.40497,-1.27149 2.13247,-1.39627 3.01207,-0.51667 0.63784,0.63784 0.95428,1.27971 0.7032,1.42637 -0.25107,0.14667 -2.95057,2.64433 -5.99889,5.55036 l -5.54238,5.28368 -4.43445,-2.01172 c -5.78388,-2.62391 -9.74025,-2.58671 -12.61999,0.11866 -2.69024,2.52736 -3.04484,6.97463 -0.71057,8.9119 1.34658,1.11757 2.071,1.06301 4.51579,-0.34011 1.60156,-0.91916 3.61733,-1.40052 4.47949,-1.06967 1.20247,0.46142 0.11271,2.06944 -4.67881,6.90393 l -6.24638,6.3024 -2.94292,-1.52184 c -1.61861,-0.83702 -4.8747,-1.59661 -7.23575,-1.68799 -5.76972,-0.22329 -8.70755,2.354 -8.29381,7.27596 0.25058,2.98093 0.71366,3.59937 2.88411,3.85167 1.42207,0.1653 3.12612,-0.35074 3.78676,-1.14677 1.13636,-1.36922 5.12764,-1.17918 5.12764,0.24414 0,0.36557 -2.5875,3.22456 -5.75,6.35331 l -5.75,5.68864 -4.46839,-1.54026 c -7.82067,-2.69579 -14.55259,0.29745 -13.85657,6.16108 0.55409,4.66785 3.4958,5.47868 8.04744,2.21814 1.29799,-0.92981 2.00585,-0.95051 2.87236,-0.084 0.86651,0.86651 0.0724,2.41283 -3.22248,6.27473 -3.71607,4.35562 -4.74761,5.02745 -6.87236,4.47592 -1.375,-0.35692 -4.80906,-0.86671 -7.63124,-1.13288 -4.40562,-0.4155 -5.43085,-0.16234 -7.25,1.79029 -2.5077,2.6917 -2.73431,6.13869 -0.54733,8.32567 2.0371,2.0371 2.96181,1.9809 5.13961,-0.31236 1.37141,-1.44411 2.34043,-1.6753 4.15166,-0.99054 l 2.36271,0.89327 -3.79871,4.74053 c -2.08929,2.60729 -3.93542,4.92344 -4.10251,5.147 -0.16709,0.22356 -2.02773,-0.37091 -4.13476,-1.32105 -5.40723,-2.43832 -10.96924,-1.78695 -13.47035,1.57753 -3.68853,4.96181 0.79842,11.39365 5.18132,7.42718 2.18166,-1.97437 4.98362,-2.05594 5.70878,-0.1662 0.30053,0.78316 -1.06359,3.81465 -3.03138,6.73665 -3.43047,5.09395 -4.52717,9.9282 -2.81249,12.39738 3.03744,4.37397 8.67842,5.13936 12.49926,1.69596 z m -5.7489,-6.34941 c 2.67153,-4.54983 6.74925,-9.97292 7.17711,-9.54506 0.58651,0.58651 -5.18943,9.21143 -6.86023,10.24404 -0.76525,0.47295 -0.86971,0.24253 -0.31688,-0.69898 z M 143,216.34237 c 0,-1.16181 8.26388,-11.41183 8.78246,-10.89324 C 152.2529,205.91956 144.1911,217 143.37839,217 143.17028,217 143,216.70407 143,216.34237 Z M 157.08659,198.5 c 0,-0.55 2.22555,-3.475 4.94567,-6.5 2.72012,-3.025 4.94568,-5.05 4.94568,-4.5 0,0.55 -2.22556,3.475 -4.94568,6.5 -2.72012,3.025 -4.94567,5.05 -4.94567,4.5 z m 16.11036,-18.15843 c 0.37347,-1.42763 10.88391,-12.59404 11.38373,-12.09422 0.19826,0.19826 -2.35016,3.26121 -5.66316,6.80656 -3.313,3.54535 -5.88726,5.9248 -5.72057,5.28766 z M 191,161.43739 c 0,-0.55 2.7,-3.67182 6,-6.93739 3.3,-3.26557 6,-5.48739 6,-4.93739 0,0.55 -2.7,3.67182 -6,6.93739 -3.3,3.26557 -6,5.48739 -6,4.93739 z M 215,137.5 c 2.98742,-3.025 5.88168,-5.5 6.43168,-5.5 0.55,0 -1.44426,2.475 -4.43168,5.5 -2.98742,3.025 -5.88168,5.5 -6.43168,5.5 -0.55,0 1.44426,-2.475 4.43168,-5.5 z m 14,-11.98123 c 0,-0.73668 4.51723,-4.67025 10.16922,-8.85528 6.13129,-4.53993 4.28305,-1.64447 -2.44895,3.83651 C 230.26274,125.75753 229,126.5784 229,125.51877 Z M 251,107.5 c 0.68469,-0.825 1.69489,-1.5 2.24489,-1.5 0.55783,0 0.44954,0.66326 -0.24489,1.5 -0.68469,0.825 -1.69489,1.5 -2.24489,1.5 -0.55783,0 -0.44954,-0.66326 0.24489,-1.5 z m 207.06884,124.37852 c 4.94479,-13.30736 9.57752,-29.23981 12.99244,-44.68233 l 3.16186,-14.29816 -2.55831,-7.19901 c -2.31506,-6.5145 -6.4256,-15.59076 -11.78779,-26.02801 -3.64604,-7.09683 -12.96909,-20.89803 -20.54861,-30.41875 -24.09878,-30.27073 -58.29925,-57.158567 -95.11588,-74.778515 -9.20141,-4.403672 -10.02418,-4.613754 -15.63413,-3.991952 -7.39071,0.819182 -25.36084,4.8292 -36.57842,8.16244 -4.675,1.38915 -10.525,3.104192 -13,3.811204 C 267.46622,45.750191 258.06252,51 263.69458,51 c 2.64372,0 24.91026,11.419225 37.14701,19.050562 11.83854,7.382995 35.31772,24.747645 49.19552,36.383848 5.20459,4.36392 17.33789,15.84417 26.96289,25.51166 35.73389,35.89164 61.18924,72.81856 75.17567,109.05393 1.19623,3.09914 1.56335,2.53091 5.89317,-9.12148 z""")

# plt.rcParams["font.family"] = "monospace"
hfont = {'family':'monospace'}

class HandlerEllipse(HandlerPatch):
    def create_artists(self, legend, orig_handle,
                       xdescent, ydescent, width, height, fontsize, trans):
        center = 0.5 * width - 0.5 * xdescent, 0.5 * height - 0.5 * ydescent
        p = mpatches.Ellipse(xy=center, width=height + xdescent,
                             height=height + ydescent)
        self.update_prop(p, orig_handle, legend)
        p.set_transform(trans)
        return [p]

year = str(2020)

# data = pd.read_csv(os.getcwd() +'\Data_Files'"\\" + 'play_by_play_' + year + '.csv', low_memory=False)
data = pd.read_csv(os.getcwd() + "\Data_Files"'\\reg_season_play_by_play_' + year + '.csv', low_memory=False)
pd.options.mode.chained_assignment = None

pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 300)

player_name = input("Receiver name: ")
title_name = player_name
first_name_char = player_name[0] + '.'
last_name = player_name.split(' ', 1)[-1]
player_name = first_name_char + last_name

if title_name == "DJ Moore":
    data = data.loc[data.posteam == "CAR"]

data = data.loc[data.receiver == player_name]
data = data.loc[data.play_type == 'pass']
data = data.loc[data.incomplete_pass == 0]
data = data.loc[~data.desc.str.contains('incomplete')]
data = data.loc[~data.desc.str.contains('No Play')]
data = data.loc[data.play_type != 'no_play']
data.reset_index(inplace=True)
data = data[data['yards_after_catch'].notnull()]
data['yardline_1'] = 100 - data['yardline_100'] + 10
# data = data.sort_values('yardline_1', ascending=False)
data['air_yards_to'] = data['yardline_1'] + data['air_yards']
data['yardline_2'] = data['yardline_1'] + data['air_yards'] + data['yards_after_catch']
# data['yardline_2'] = data['yardline_1'] + data['yards_gained']
data['sortable'] = data['yardline_2'] - data['yardline_1']
# data = data.sort_values(['yardline_1', 'yardline_2'], ascending=[True, True])
data = data.sort_values(['sortable', 'yardline_1'], ascending=[False, True])
data.reset_index(inplace=True)
data['catch_number'] = data.index.values + 1
data['catch_number'] = data['catch_number'] * (50/len(data))
data['catch_number'] = data['catch_number'] + 1.65

fig, ax = plt.subplots(figsize=(15,15))

# Set field dimensions
plt.xlim(0, 120)  # Field length including endzones
plt.ylim(0, 53.3)  # field width

# Set field color green
ax.set_facecolor('#79af75')
ax.set_alpha(0.5)
# ax.fill_between(np.arange(0,10,0.1), 0, 53.3, facecolor=COLORS2[data['posteam'].iloc[0]])
# ax.fill_between(np.arange(110,120,0.1), 0, 53.3, facecolor=COLORS2[data['posteam'].iloc[0]])

# Print lines
for i in range(0, 120, 5):
    if i != 5 and i != 115:
        plt.axvline(i, color='white', linewidth=3, alpha=0.4, zorder=0)
    if i == 10 or i == 110:  # Make endzone lines
        plt.axvline(i, color='white', linewidth=5, alpha=0.4, zorder=1)

# Paint numbers
yds_from_sideline = 12
for i in range(10, 50, 10):
    plt.text(i+9.5, 53.3-yds_from_sideline, str(i), color='white', fontsize=20, verticalalignment='bottom', horizontalalignment='center', rotation=180)
    plt.text(109.5-i, 53.3-yds_from_sideline,  str(i), color='white', fontsize=20, verticalalignment='bottom', horizontalalignment='center', rotation=180)

    plt.text(i+10, yds_from_sideline, str(i), color='white', fontsize=20, verticalalignment='bottom', horizontalalignment='center')
    plt.text(110-i, yds_from_sideline, str(i), color='white', fontsize=20, verticalalignment='bottom', horizontalalignment='center')

for i in range(0, 50, 1):
    if i % 5 == 0:
        continue
    plt.text(109.6-i, 53.3-1,  "l", color='white', fontsize=15, verticalalignment='bottom', horizontalalignment='center', rotation=180, alpha=0.4, zorder=1)
    plt.text(109.5-i, 0,  "l", color='white', fontsize=15, verticalalignment='bottom', horizontalalignment='center', rotation=180, alpha=0.4, zorder=1)
    plt.text(i+9.7, 0, "l", color='white', fontsize=15, verticalalignment='bottom',
             horizontalalignment='center', rotation=180, alpha=0.4, zorder=1)
    plt.text(i+9.7, 53.3-1, "l", color='white', fontsize=15, verticalalignment='bottom',
             horizontalalignment='center', rotation=180, alpha=0.4, zorder=1)

# Paint 50 yard line numbers
plt.text(60, 53.3-yds_from_sideline, str(50), color='white', fontsize=20, verticalalignment='bottom', horizontalalignment='center', rotation=180)
plt.text(60, yds_from_sideline, str(50), color='white', fontsize=20, verticalalignment='bottom', horizontalalignment='center')

LeftColor = COLORS[data['posteam'].iloc[0]]
RightColor = COLORS[data['posteam'].iloc[0]]
plt.text(5, 26.5, TEAMS[data['posteam'].iloc[0]], color=LeftColor, fontsize=30, verticalalignment='center', horizontalalignment='center', rotation=90)
plt.text(115, 26.5, TEAMS[data['posteam'].iloc[0]], color=RightColor, fontsize=30, verticalalignment='center', horizontalalignment='center', rotation=270)

team_logo = (os.getcwd() + "\Team_Logos"'\\' + data['posteam'].iloc[0] + '.png')
team_logo = plt.imread(team_logo)
team_logo = OffsetImage(team_logo, zoom=0.50)
team_logo.set_offset((735, 375))
ax.add_artist(team_logo)

ax.scatter(data['air_yards_to'], data['catch_number'], color='y')
ax.scatter(data['yardline_1'], data['catch_number'], color='b')
ax.scatter(data['yardline_2'], data['catch_number'], color='r')


for x in range(0, len(data)):
    ax.hlines(y=data['catch_number'].iloc[x], xmin=data['yardline_1'].iloc[x], xmax=data['air_yards_to'].iloc[x], color='b')
    ax.hlines(y=data['catch_number'].iloc[x], xmin=data['air_yards_to'].iloc[x], xmax=data['yardline_2'].iloc[x], color='y')
    if data.pass_touchdown.iloc[x] == 1:
        ax.scatter(data['yardline_2'].iloc[x], data['catch_number'].iloc[x], color='g')

plt.xticks([])
plt.yticks([])

# plt.suptitle(title_name + ' 2019 Receptions Chart',fontsize=20)
ax.set_title(title_name + ' ' + year + ' Receptions Chart' + "\n" + "by Jake Sanghavi",fontsize=20,pad=15, **hfont)
# ax.set_title('Stats: Receptions=' + str(int(len(data))) + ', Yards=' + str(int(data['air_yards'].sum()) + int(data['yards_after_catch'].sum())) + ', AY=' + str(int(data['air_yards'].sum())) + ', YAC=' + str(int(data['yards_after_catch'].sum())) + ', TD=' + str(int(data['pass_touchdown'].sum())), fontsize=10)
# ax.text(60,54,'Stats: Receptions=' + str(int(len(data))) + ', Yards=' + str(int(data['air_yards'].sum()) + int(data['yards_after_catch'].sum())) + ', AY=' + str(int(data['air_yards'].sum())) + ', YAC=' + str(int(data['yards_after_catch'].sum())) + ', TD=' + str(int(data['pass_touchdown'].sum())), fontsize=10, horizontalalignment='center')

# plt.savefig('receiver_graph_test.png',dpi=400)

plt.text(87.5,-3,"Base field design credit: @Pavel_Vab" + "\n" + "Data: nflfastR", **hfont)
plt.text(2.5,-1.8,TAGS[data['posteam'].iloc[0]], fontsize=12, **hfont)
# cmap = plt.cm.coolwarm
# custom_lines = [Line2D(range(1), range(1), color='b', marker='o'),
#                 Line2D([0], [0], color='y', lw=4),
#                 Line2D([0], [0], color='r', lw=4),
#                 Line2D([0], [0], color='g', lw=4)]
#
# ax.legend(custom_lines, ['Line of Scrimmage', 'Point of Catch', 'Tackled', 'Touchdown'])
c = [mpatches.Circle((0.5, 0.5), radius=0.25, facecolor='b', edgecolor="none"), mpatches.Circle((0.5, 0.5), radius=0.25, facecolor='y', edgecolor="none"),
     mpatches.Circle((0.5, 0.5), radius=0.25, facecolor='r', edgecolor="none"), mpatches.Circle((0.5, 0.5), radius=0.25, facecolor='g', edgecolor="none")]
labels = ['Line of Scrimmage', 'Point of Catch', 'Tackled', 'Touchdown']
leg = ax.legend(c, labels, title="Key:", loc='upper left', handler_map={mpatches.Circle: HandlerEllipse()}, fancybox=True)
# leg._legend_box.align = "left"
leg.get_title().set_position((-62, 0))

plt.show()

