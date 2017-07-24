heat_yeardens <- function(values, years, ylims, xlims, colbins, ylab, minlimit=10) {
  
  langdf <- data.frame(values = values, year = years)
  langdf <- subset(langdf, is.na(langdf$values) != 1 | is.na(langdf$year) != 1)
  
  # Color
  rf <- viridis::inferno(1000)
  
  dens1d_x <- seq(from=ylims[1], to=ylims[2], length.out=colbins)
  
  array_x <- xlims[1]:xlims[2]
  array_y <- dens1d_x
  array_z <- matrix(nrow = colbins, ncol=length(array_x))
  
  for(i in 1:length(array_x)) {
    
    k <- subset(langdf, langdf$year==array_x[i])
    
    if(nrow(k) > minlimit) {
      array_z[,i] = density(k$values, from = ylims[1], to = ylims[2], n = colbins)$y
    } else { array_z[,i] = rep(0, colbins) }
  }
  
  array_z[is.na(array_z)] = 0
  
  one_d_list_outcome <- list(x = array_x, y = array_y, z = t(array_z))
  
  return(image(one_d_list_outcome, col=rf, xlab = 'Year', ylab = ylab, useRaster = T))
  
}