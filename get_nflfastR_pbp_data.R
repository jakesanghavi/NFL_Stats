# Load the required packages
library(nflfastR)
library(tidyverse)

# Load the play by play data of your desired season. Note that this includes
# penalties, no-plays, special teams, and postseason games.
pbp_2022 <- load_pbp(2022)

# Write the play by play data to your desired path.
write.csv(pbp_2022, file = "nfl_2022_pbp.csv",row.names=FALSE)
