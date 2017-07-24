#' Percentage Data Limits
#'
#' Function to calculate axis limits for plots displaying large amounts of data with large spread.  
#' This function optimises the xlim and ylim parameters of the final plot in order to include at 
#' least a certain percentage of the data points, while minimising the extent of the x and y axes.
#'
#' @param x X values
#' @param y Y values
#' @param perc The percentage of points which should be included in the final figure
#' @param xlo.start Specify the starting parameter for xlo
#' @param xhi.start Specify the starting parameter for xhi
#' @param ylo.start Specify the starting parameter for ylo
#' @param yhi.start Specify the starting parameter for yhi
#'
#' @return Returns the x limits and the y limits for the new plot
#'
#' @examples
#' 
#' x <- rnorm(1000)
#' y <- rnorm(1000)
#' 
#' percdata_lim(x,y,90)
#'
#' @export

percdata_lim <- function(x, y, perc, xlo.start=NULL, xhi.start=NULL, ylo.start=NULL, yhi.start=NULL) {
  
  if(is.null(xlo.start)) xlo.start <- min(x)
  if(is.null(xhi.start)) xhi.start <- max(x)
  if(is.null(ylo.start)) ylo.start <- min(y)
  if(is.null(yhi.start)) yhi.start <- max(y)

  outpar <- optim(par = c(xlo=xlo.start, xhi=xhi.start, ylo=ylo.start, yhi=yhi.start), fn = percdata_model, x=x,y=y,perc=perc, control = list(fnscale=-1))
  
  xlim <- outpar$par[1:2]
  ylim <- outpar$par[3:4]
  
  out <- list(xlim = xlim, ylim = ylim)
  return(out)
}

percdata_model <- function(par, x, y, perc) {
  if(length(x) != length(y)) { stop('x and y vectors are not of equal length') }
  
  inlim <- 100 * sum(x >= par[1] & x <= par[2] & y >= par[3] & y <= par[4]) / length(x)
  cost <- ifelse(inlim < perc, Inf, (par[2]-par[1])*(par[3]-par[4]))
  return(cost)
}