library('RJSONIO')

setwd(choose.dir())

yr <- 2020
print(dir)
#all_json <- c(dir(paste0('Sportradar/',yr), full=T),dir(paste0('Sportradar/post/',yr), full=T))
all_json <- dir(paste0('SportRadar/',yr), full=T)

all_col_names <- c('qtr', 'drv', 'play_ref', 'play_id', 'play_type', 'playtime', 'playclock', 'screen_pass', 'hash_mark', 'play_direction', 'men_in_box',
                   'blitz', 'left_tightends', 'right_tightends', 'qb_at_snap', 'play_action', 'run_pass_option', 'running_lane', 'rush_yards_after_contact',
                   'broken_tackles', 'players_rushed', 'pass_route', 'qb_on_target', 'qb_hurry', 'qb_knockdown', 'pocket_time', 'pocket_location', 'rec_drop',
                   'rec_catchable', 'def_tar_ID.reference', 'incompletion_type', 'pass_batted', 'rec_yards_after_contact', 'rec_broken_tackles', 'game_file',
                   'squib_kick', 'onside_attempt', 'onside_success')

df_list <- lapply(all_json, function(x) {
  pbp_json <- fromJSON(x)
  
  full_pbp <- lapply(pbp_json$periods, function(qtr) {
    lapply(qtr$pbp, function(drv) {
      lapply(drv$events, function(ply) {
        stat_types <- sapply(ply$statistics, function(x) x$stat_type)
        rush_stat <- NA
        pass_stat <- NA
        rec_stat <- NA
        kick_stat <- NA
        def_tar_ID <- NA
        if (!is.na(match('rush',stat_types))) {
          rush_stat <- match('rush',stat_types)
        }
        if (!is.na(match('pass',stat_types))) {
          pass_stat <- match('pass',stat_types)
        }
        if (!is.na(match('receive',stat_types))) {
          rec_stat <- match('receive',stat_types)
        }
        if (!is.na(match('kick',stat_types))) {
          kick_stat <- match('kick',stat_types)
        }
        
        if (!is.na(match('defense',stat_types))) {
          def_stat <- match('defense',stat_types)
          def_tar_ID <- def_stat[match(1,sapply(def_stat, function(x) ply$statistics[[x]]$def_target))]
        }
        return(c(
          'qtr'=qtr$number,
          'drv'=drv$sequence,
          'play_ref'=ply$reference,
          'play_id'=ply$id,
          'play_type'=ply$play_type,
          'play_direction'=ply$play_direction,
          'playtime'=ply$wall_clock,
          'playclock'=ply$play_clock,
          'men_in_box'=ply$men_in_box,
          'screen_pass'=ply$screen_pass,
          'blitz'=ply$blitz,
          'players_rushed'=ply$players_rushed,
          'hash_mark'=ply$hash_mark,
          'left_tightends'=ply$left_tightends,
          'right_tightends'=ply$right_tightends,
          'running_lane'=ply$running_lane,
          'qb_at_snap'=ply$qb_at_snap,
          'play_action'=ply$play_action,
          'run_pass_option'=ply$run_pass_option,
          'rush_yards_after_contact'=ply$statistics[[rush_stat]]$yards_after_contact,
          'broken_tackles'=ply$statistics[[rush_stat]]$broken_tackles,
          'pass_route'=ply$pass_route,
          'incompletion_type'=ply$statistics[[pass_stat]]$incompletion_type,
          'qb_on_target'=ply$statistics[[pass_stat]]$on_target_throw,
          'pass_batted'=ply$statistics[[pass_stat]]$batted_pass,
          'qb_hurry'=ply$statistics[[pass_stat]]$hurry,
          'qb_knockdown'=ply$statistics[[pass_stat]]$knockdown,
          'pocket_time'=ply$statistics[[pass_stat]]$pocket_time,
          'pocket_location'=ply$pocket_location,
          'rec_drop'=ply$statistics[[rec_stat]]$dropped,
          'rec_catchable'=ply$statistics[[rec_stat]]$catchable,
          'rec_yards_after_contact'=ply$statistics[[rec_stat]]$yards_after_contact,
          'rec_broken_tackles'=ply$statistics[[rec_stat]]$broken_tackles,
          'def_tar_ID'=ply$statistics[[def_tar_ID]]$player['reference'],
          'squib_kick'=ply$statistics[[kick_stat]]$squib_kick,
          'onside_attempt'=ply$statistics[[kick_stat]]$onside_attempt,
          'onside_success'=ply$statistics[[kick_stat]]$onside_success
        ))
      })
    })
  })
  
  full_pbp <- unlist(unlist(full_pbp,recursive = F),recursive = F)
  full_pbp <- lapply(full_pbp, function(ply) {
    return(ply[match(all_col_names, names(ply))])
  })
  
  full_pbp_df <- data.frame(do.call(rbind, full_pbp),stringsAsFactors = F)
  names(full_pbp_df) <- all_col_names
  #full_pbp_df$game_file <- gsub('.json','',strsplit(gsub('2019','',x),'/')[[1]][3])
  full_pbp_df$game_file <- gsub('.json','',sapply(strsplit(gsub('2018','',x),'/'), function(y) rev(y)[1]))
  #full_pbp_df$game_year <- strsplit(x,'/')[[1]][2]
  
  return(full_pbp_df)
})

all_gm_df <- do.call(rbind, df_list)
#str(all_gm_df)

#Replcae this path with the directory in which you SportRadar pbp file is saved
write.csv(all_gm_df, paste0('DoNotModify/SportRadar_full_',yr,'.csv'), row.names=F)

#Replace this path with the directory in which you schedule file is saved.
sched_json <- fromJSON(paste0('DoNotModify/api_schedule_',yr,'.json'))

gms_list <- lapply(sched_json$weeks, function(wk) {
  t(sapply(wk$games, function(gm) {
    c(
      'week'=wk$title,
      'home_tm'=gm$home$alias,
      'away_tm'=gm$away$alias,
      'game_id'=gm$id
    )}))	
})
sport_gm_df <- data.frame(do.call(rbind, gms_list), stringsAsFactors=F)

str(sport_gm_df)

#sched_json_post <- fromJSON(paste0('Sportradar/sched/',yr,'_PST.json'))

#gms_list <- lapply(sched_json_post$weeks, function(wk) {
  #t(sapply(wk$games, function(gm) {
    #c(
      #'week'=wk$title,
      #'home_tm'=as.character(gm$home['alias']),
      #'away_tm'=as.character(gm$away['alias']),
      #'game_id'=gm$id
    #)}))	
#})
#sport_gm_post_df <- data.frame(do.call(rbind, gms_list), stringsAsFactors=F)
#sport_gm_post_df$week <- 18

#sport_gm_df <- rbind(sport_gm_df, sport_gm_post_df)

#scrp_gm_df <- read.csv(paste0('DoNotModify/regular_season_play_by_play_',yr,'.csv'), stringsAsFactors=F)

#Replace this path with where your nflfastr game_ids are saved.
scrp_gm_df <- read.csv(paste0('DoNotModify/nflfastr_',yr,'_game_ids.csv'), stringsAsFactors=F)

str(scrp_gm_df)

#scrp_gm_post_df <- read.csv(paste0('games/post/post_games_',yr,'.csv'), stringsAsFactors=F)
#scrp_gm_df <- rbind(scrp_gm_df,scrp_gm_post_df)

sport_gm_df$home_tm[which(sport_gm_df$home_tm=='JAC')] <- 'JAX'
sport_gm_df$away_tm[which(sport_gm_df$away_tm=='JAC')] <- 'JAX'
sport_gm_df$home_tm[which(sport_gm_df$home_tm=='OAK')] <- 'LV'
sport_gm_df$away_tm[which(sport_gm_df$away_tm=='OAK')] <- 'LV'
sport_gm_df$home_tm[which(sport_gm_df$home_tm=='SDG')] <- 'LAC'
sport_gm_df$away_tm[which(sport_gm_df$away_tm=='SDG')] <- 'LAC'
sport_gm_df$home_tm[which(sport_gm_df$home_tm=='SD')] <- 'LAC'
sport_gm_df$away_tm[which(sport_gm_df$away_tm=='SD')] <- 'LAC'
sport_gm_df$home_tm[which(sport_gm_df$home_tm=='STL')] <- 'LA'
sport_gm_df$away_tm[which(sport_gm_df$away_tm=='STL')] <- 'LA'

#full_gm_df <- sport_gm_df
full_gm_df <- merge(sport_gm_df, scrp_gm_df, by.x = c('week', 'home_tm', 'away_tm'), by.y = c('week', 'home_team', 'away_team'), all.x = T, suffix = c('_sprt','_scrp'))
### games where scraper doesn't have (always pro bowl)
#full_gm_df[which(is.na(full_gm_df$game_id_scrp)),]
str(full_gm_df)

all_gm_df <- read.csv(paste0('DoNotModify/SportRadar_',yr,'.csv'), stringsAsFactors=F)
str(all_gm_df)
##get correct gameID
all_gm_df <- merge(all_gm_df, full_gm_df[,c('game_id_sprt','game_id_scrp')], by.x = c('game_file'), by.y = c('game_id_sprt'), all.x=T)
str(all_gm_df)
### games where plays are being ignored (always pro bowl)
unique(all_gm_df$game_file[which(is.na(all_gm_df$game_id_scrp))])

#Replace this path with where you nflfastR pbp data is saved.
same_yr_pbp <- read.csv(paste0('DoNotModify/reg_season_play_by_play_',yr,'.csv'),stringsAsFactors = F)
str(same_yr_pbp)
#same_yr_pbp <- readRDS(paste0('C:/Users/Owner/Documents/nflfastR-data/pbp/play_by_play_',yr,'.rds'))
all_in_pbp <- merge(same_yr_pbp, all_gm_df, by.x = c('game_id', 'play_id'), by.y = c('game_id_scrp', 'play_ref'), all.x = T, suffix = c('','_sportradar'))
str(all_in_pbp)
#saveRDS(all_in_pbp, paste0('full pbp/',yr,'.rds'))

#Replace this path with your desired file destination
write.csv(all_in_pbp, paste0('DoNotModify/reg_pbp_and_sportradar_',yr,'.csv'), row.names=F)

