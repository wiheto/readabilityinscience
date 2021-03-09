smoothScatter_densout <- function (x, y = NULL, nbin = 128, bandwidth, colramp = colorRampPalette(c("white", 
                                                                                                   blues9)), nrpoints = 100, ret.selection = FALSE, pch = ".", 
                                  cex = 1, col = "black", transformation = function(x) x^0.25, 
                                  postPlotHook = NULL, xlab = NULL, ylab = NULL, xlim, ylim, 
                                  xaxs = par("xaxs"), yaxs = par("yaxs"), ...) 
{
  
  # Please note that this is a modification of the smoothScatter() function in order to extract the density values
  
  if (!is.numeric(nrpoints) || nrpoints < 0 || length(nrpoints) != 
      1) 
    stop("'nrpoints' should be numeric scalar with value >= 0.")
  xydat <- data.frame(xvals = x, yvals = y)
  nrpoints <- round(nrpoints)
  ret.selection <- ret.selection && nrpoints > 0
  xlabel <- if (!missing(x)) 
    deparse(substitute(x))
  ylabel <- if (!missing(y)) 
    deparse(substitute(y))
  xy <- xy.coords(x, y, xlabel, ylabel)
  xlab <- if (is.null(xlab)) 
    xy$xlab
  else xlab
  ylab <- if (is.null(ylab)) 
    xy$ylab
  else ylab
  x <- cbind(xy$x, xy$y)[I <- is.finite(xy$x) & is.finite(xy$y), 
                         , drop = FALSE]
  if (ret.selection) 
    iS <- which(I)
  if (!missing(xlim)) {
    stopifnot(is.numeric(xlim), length(xlim) == 2, is.finite(xlim))
    x <- x[I <- min(xlim) <= x[, 1] & x[, 1] <= max(xlim), 
           , drop = FALSE]
    if (ret.selection) 
      iS <- iS[I]
  }
  else {
    xlim <- range(x[, 1])
  }
  if (!missing(ylim)) {
    stopifnot(is.numeric(ylim), length(ylim) == 2, is.finite(ylim))
    x <- x[I <- min(ylim) <= x[, 2] & x[, 2] <= max(ylim), 
           , drop = FALSE]
    if (ret.selection) 
      iS <- iS[I]
  }
  else {
    ylim <- range(x[, 2])
  }
  map <- grDevices:::.smoothScatterCalcDensity(x, nbin, bandwidth)
  xm <- map$x1
  ym <- map$x2
  dens <- map$fhat
  dens[] <- transformation(dens)
  image(xm, ym, z = dens, col = colramp(256), xlab = xlab, 
        ylab = ylab, xlim = xlim, ylim = ylim, xaxs = xaxs, yaxs = yaxs, 
        ...)
  if (!is.null(postPlotHook)) 
    postPlotHook()
  if (nrpoints > 0) {
    nrpoints <- min(nrow(x), ceiling(nrpoints))
    stopifnot((nx <- length(xm)) == nrow(dens), (ny <- length(ym)) == 
                ncol(dens))
    ixm <- 1L + as.integer((nx - 1) * (x[, 1] - xm[1])/(xm[nx] - 
                                                          xm[1]))
    iym <- 1L + as.integer((ny - 1) * (x[, 2] - ym[1])/(ym[ny] - 
                                                          ym[1]))
    sel <- order(dens[cbind(ixm, iym)])[seq_len(nrpoints)]
    x <- x[sel, , drop = FALSE]
    points(x, pch = pch, cex = cex, col = col)
    if (ret.selection) 
      iS[sel]
  }
  nValues <- nrow(subset(xydat, xydat$xvals >= xlim[1] & xydat$xvals <= xlim[2] &
                           xydat$yvals >= ylim[1] & xydat$yvals <= ylim[2]))
  pointfraction <- nValues / length(xydat$xvals)
  abc2 <- nValues/sum(dens^4) * (dens^4)
  colmax = max(abc2)
  colmin = min(abc2)
  colsum = sum(abc2)
  out <- list(dens = dens, pointfraction=pointfraction, nValues=nValues, max=colmax, min=colmin, sum=colsum)
  return(out)
}