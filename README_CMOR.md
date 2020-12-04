# PGW-Simulation for CMOR input data

This is an attempt at a very practical explaination of how to set up a PGW simulation using Global Climate Model data in the CMOR-Format as input (for example CMIP5 or CMIP6 data).

**What data to get?**

You will need data for the following variables: hur, hurs, ta, tas, ua, va

**What time resolution should one choose?**

Monthly mean data is the easyiest. This is called Amon in CMOR.

**How to preprocess the data?**

For all variables (hur, hurs, ta, tas, ua, va) we need to know how they will change under climate change. This needs to be expressed as a mean annual cycle of changes.
In practice we can get a time slice of the "hisorical" period and from a future period under a certain emission scenario such as "rcp85". A typical example: For the historical period, get data from 1971-2000. Then construct the mean annual cycle using the cdo-command "ymonmean". Repeat for 2070-2099 and the rcp85 data. Lastly, subtract the historical monthly-mean annual cycle from the future monthly-mean annual cycle.
