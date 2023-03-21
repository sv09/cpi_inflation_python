# IMPORT REQUIRED LIBRARIES
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re


# DICTIONARY FOR ACCESSING MONTH NUMBER
month_id = {"Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, "Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}


# HELPER FUNCTIONS

## return percentage change YOY
def get_yoy_pct_change(df):
  j=0
  for i in range(1, 13):
    df.loc[j, "Pct_Change"] = 0
    j+=1
    m = df.loc[j, "Month"]
    month = df.loc[j, "Month"]
    while month == m:
      year = df.loc[j, "Year"]
      this_year = df.loc[j, "Value"]
      last_year = df.loc[j-1, "Value"]
      pct_chnge = ((this_year/last_year) - 1)
      df.loc[j, "Pct_Change"] = pct_chnge
      if (j+1) < len(df):
        j+=1
      else:
        break
      month = df.loc[j, "Month"]
  return df

## create month_num + year as id 
def create_id(df):
  for i in range(len(df)):
    m = df.loc[i, "month_num"]
    y = df.loc[i, "Year"]
    id = str(m) + '_' + str(y)
    df.loc[i, "id"] = id
  return df


# DATA FROM 1965 TO PRESENT
cpi_u_data = pd.read_csv("./data/bls_1965_2023_cpi_u.csv")
cpi_less_food_energy_data = pd.read_excel("./data/bls_cpi_less_food_energy.xlsx", skiprows=11)


# PREP DATA FOR VISUALIZATION

## cpi_u_data 

for i in range(len(cpi_u_data)):
  period = cpi_u_data.loc[i, "Period"]
  period = period.replace("M", '')
  if period[0] == '0':
    num = period.replace('0', '')
  else:
    num = period

  month_num = int(num)
  month = list(month_id.keys())[list(month_id.values()).index(month_num)]
  cpi_u_data.loc[i, "Month"] = month
  cpi_u_data.loc[i, "month_num"] = month_num

# create id
cpi_u_data = create_id(cpi_u_data)

# sort data for by month first and year for calculating yoy percent change
cpi_u_data_sort = cpi_u_data.sort_values(by=["month_num", "Year"], ascending=True)

# drop columns that are not needed
cpi_u_data_sort = cpi_u_data_sort.drop(columns=["Series ID", "Label", "Period"])

# reset index
cpi_u_data_sort = cpi_u_data_sort.reset_index(drop=True)

# get yoy percent change 
cpi_u_data_sort = get_yoy_pct_change(cpi_u_data_sort)

# drop any row with NA
cpi_u_data_sort = cpi_u_data_sort.dropna()

# reset index
cpi_u_data_sort = cpi_u_data_sort.reset_index(drop=True)

# plot data by yera and then month for plotting in chronological order
cpi_u_df = cpi_u_data_sort.sort_values(by=["Year", "month_num"])

# reset index
cpi_u_df = cpi_u_df.reset_index(drop=True)



## cpi_less_food_energy_data


# drop columns that are not needed
cpi_less_food_energy_data = cpi_less_food_energy_data.drop(columns=["HALF1", "HALF2"])

# melt df into desired format
cpi_less_food_energy_data = cpi_less_food_energy_data.melt(id_vars=["Year"], 
        var_name="Month", 
        value_name="Value")

# create month number as a column
for i in range(len(cpi_less_food_energy_data)):
  month = cpi_less_food_energy_data.loc[i, "Month"]
  cpi_less_food_energy_data.loc[i, "month_num"] = month_id[month]

# create id
cpi_less_food_energy_data = create_id(cpi_less_food_energy_data)

# sort data for by month first and year for calculating yoy percent change
cpi_less_food_energy_data_sort = cpi_less_food_energy_data.sort_values(by=["month_num", "Year"], ascending=True)

# get yoy percent change 
cpi_less_food_energy_data_sort = get_yoy_pct_change(cpi_less_food_energy_data_sort)

# drop any row with NA
cpi_less_food_energy_data_sort = cpi_less_food_energy_data_sort.dropna()

# reset index
cpi_less_food_energy_data_sort = cpi_less_food_energy_data_sort.reset_index(drop=True)

# plot data by yera and then month for plotting in chronological order
cpi_less_food_energy_df = cpi_less_food_energy_data_sort.sort_values(by=["Year", "month_num"])

# reset index
cpi_less_food_energy_df = cpi_less_food_energy_df.reset_index(drop=True)


## PLOT

fig, ax = plt.subplots(figsize = (12, 5))

ax.plot(cpi_less_food_energy_df["id"], cpi_less_food_energy_df["Pct_Change"], color="#C8D2D6", linewidth=1.2)
ax.plot(cpi_u_df["id"], cpi_u_df["Pct_Change"], color="#575A5C", linewidth=1.2)

xlabels = list(cpi_u_df["Year"])
ax.set(xticklabels = (xlabels))

y_vals = [min(cpi_u_df["Pct_Change"]), min(cpi_less_food_energy_df["Pct_Change"]), max(cpi_u_df["Pct_Change"]), max(cpi_less_food_energy_df["Pct_Change"])]
y_val_range = [round((min(y_vals)*100)), round((max(y_vals)*100))]
y_tick_labels = np.arange(y_val_range[0], y_val_range[1], 2)

total_y_ticks = len(ax.get_yticklabels())

ylabels=[]
for ylabel in ax.get_yticklabels():
	yval = ylabel.get_text()
	if yval[0] == '−':
		yval = yval.replace('−', '')
		num = float(yval)*-1
	else:
		num = float(yval)
	ylabels.append(round(num*100))


# make values in the ylabels even for consistency and add '+' sign for positive numbers
for i in range(len(ylabels)):
	val = ylabels[i]
	if val%2 != 0:
		if val < 0:
			val = val+1
			ylabels[i] = '- ' + str(val*(-1))
		else:
			ylabels[i] = '+ ' + str(val-1)
	elif val == 0:
		ylabels[i] = str(val)
	else:
		if val < 0:
			ylabels[i] = '- ' + str(val*(-1))
		else:
			ylabels[i] = '+ ' + str(val)


ax.set(yticklabels = (ylabels))


ax.tick_params(axis='both', labelcolor='black', labelsize=6 , color='white', grid_linestyle='dotted')
ax.yaxis.grid(True)
ax.axhline(y=0, linestyle='solid', linewidth=0.9, color='gray')

itr=0
for xlabel in ax.get_xticklabels():
	if itr%12 == 0:
		year = int(xlabel.get_text())
		if year%5 == 0:
			xlabel.set_visible(True)
		else:
			xlabel.set_visible(False)
	else:
		xlabel.set_visible(False)
	itr+=1


ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.spines["bottom"].set_visible(False)

ax.set_ylabel("Percent Change", fontsize=8)
fig.suptitle('Inflation Trend: 1965-Present', fontsize=11.5, fontfamily='sans-serif')

plt.text(0.6, 0.78, 'Inflation',
     horizontalalignment='center',
     verticalalignment='center',
     fontfamily='sans-serif',
     fontsize=11.5,
     fontweight='bold',
     color='#575A5C',
     transform = ax.transAxes)

# plt.text(0.2, 0, 'Year-over-year percentage change in the Consumer Price Index | Source: Bureau of Labor Statistics',
# 		horizontalalignment='center',
# 	     verticalalignment='center',
# 	     transform = ax.transAxes, fontsize=6, color='gray')

ax.set_xlabel('Year-over-year percentage change in the Consumer Price Index | Source: Bureau of Labor Statistics', fontsize=6, color='gray', loc="left")


## PLOT ANNOTATION

# cpi_u_df

last_x_1 = cpi_u_df.index[cpi_u_df["Year"] == 2023][0]
last_y_1 = cpi_u_df.loc[last_x_1, "Pct_Change"]
last_val_month_1 =cpi_u_df.loc[last_x_1, "Month"]
txt_val_1 = str(round(last_y_1*100, 2))
if float(txt_val_1) > 0:
	sign = "+"
elif float(txt_val_1) < 0:
	sign = "-"



annot_txt_1 = sign + txt_val_1  + "%"+ " in " + last_val_month_1

ax.plot([last_x_1], [last_y_1], 'o', color='#575A5C', markersize=4)
txt_x_1 = last_x_1+5
txt_y_1 = last_y_1
ax.annotate(annot_txt_1, xy=(last_x_1, last_y_1), xytext=(txt_x_1, txt_y_1))


# cpi_less_food_energy_df

last_x_2 = cpi_less_food_energy_df.index[cpi_less_food_energy_df["Year"] == 2023][0]
last_y_2 = cpi_less_food_energy_df.loc[last_x_2, "Pct_Change"]
last_val_month_2 = cpi_less_food_energy_df.loc[last_x_2, "Month"]
txt_val_2 = str(round(last_y_2*100, 2))
if float(txt_val_2) > 0:
	sign = "+"
elif float(txt_val_2) < 0:
	sign = "-"

annot_txt_2 = sign + txt_val_2 +  "%" + "\n" + " excluding food " + "\n" + " and energy"

ax.plot([last_x_2], [last_y_2], 'o', color='#C8D2D6', markersize=4)
txt_x_2 = last_x_2+5
txt_y_2 = last_y_2-0.02
ax.annotate(annot_txt_2, xy=(last_x_2, last_y_2), xytext=(txt_x_2, txt_y_2))


plt.show()





