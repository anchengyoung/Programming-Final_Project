library(RSQLite)
library(ggplot2)

con = dbConnect(drv=SQLite(),dbname="farebox.db")
df.farebox <- dbGetQuery(con, "SELECT * FROM farebox_ratio;")

ggplot(data = df.farebox, aes(x = ratio)) +
  geom_density()

df.flat_rate <- dbGetQuery(con, "SELECT * FROM farebox_ratio WHERE fare_system = 'Flat rate';")

ggplot(data = df.flat_rate, aes(x = ratio, y = us_rate)) +
  geom_point()

ggplot(data = df.farebox, aes(x = ratio)) +
  geom_density() + facet_wrap(~fare_system, ncol = 4)

ggplot(data = df.farebox, aes(x = ratio)) +
  geom_density() + facet_wrap(~continent, ncol = 4)

ggplot(data = df.farebox, aes(x = ratio)) +
  geom_histogram(binwidth = 20) + facet_wrap(~year, ncol = 4)

df.continent <- dbGetQuery(con, "SELECT continent, avg(ratio) AS ratio, avg(year) AS year FROM farebox_ratio GROUP BY continent;")

ggplot(data = df.continent, aes(x = year, y = ratio)) +
  geom_point() + geom_text(aes(label = continent), vjust = 2) +
  xlim(2008, 2016) + ylim(30, 100)

df.has_rate <- dbGetQuery(con, "SELECT * FROM farebox_ratio WHERE us_rate != 'NA';")

lm_eqn <- function(df.has_rate){
  m <- lm(ratio ~ us_rate, df.has_rate);
  eq <- substitute(italic(r)^2~"="~r2, 
                   list(r2 = format(summary(m)$r.squared, digits = 3)))
  as.character(as.expression(eq));                 
}

ggplot(data = df.has_rate, aes(x = us_rate, y = ratio)) +
  geom_point() + geom_smooth(method = lm, se = FALSE) + 
  geom_text(x = 4, y = 100, label = lm_eqn(df.has_rate), parse = TRUE)

ggplot(data = df.has_rate, aes(x = us_rate, y = ratio)) +
  geom_point() + geom_smooth(method = lm, se = FALSE) + 
  facet_wrap(~continent, ncol = 4)

ggplot(data = df.has_rate, aes(x = us_rate, y = ratio)) +
  geom_point() + geom_smooth(method = lm, se = FALSE) +
  facet_wrap(~fare_system, ncol = 4)
