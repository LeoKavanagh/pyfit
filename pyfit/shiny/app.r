library(shiny)
library(shinydashboard)
library(ggplot2)

options(shiny.port = 8888)

ui <- dashboardPage(
  dashboardHeader(title = "Fit"),

  dashboardSidebar(
    sidebarMenu(
      menuItem("Dashboard", tabName = "dashboard", icon = icon("dashboard")),
      menuItem("Widgets", tabName = "widgets", icon = icon("th")),
      menuItem("Another thing", tabName = "anotherThingTabName", icon = icon("balance-scale"))
    )
  ),

  dashboardBody(
    tabItems(
      # First tab content
      tabItem(tabName = "dashboard",
        fluidRow(
          box(plotOutput("plot1", height = 250)),

          box(
            title = "Controls",
            sliderInput("slider", "Number of observations:", 1, 100, 50)
          )
        ),

	fluidRow(
	  box(plotOutput("plot2", height = 250)),

	  box(
	    title = "Scatter plot controls",
	    sliderInput("scatterPlotSlider", "Number of observations", 1, 100, 50)
	  )
	)),

      # Second tab content
      tabItem(tabName = "widgets", h2("Widgets tab content"))
    )
  )
)


server <- function(input, output) {
  set.seed(122)
  histdata <- rnorm(500)

  data_df = read.csv('google_training_data.csv')
  data_df$date = as.Date(data_df$date)

  # plot1, plot2 and slider are named as strings in ui
  output$plot1 <- renderPlot({
    ggplot(data_df, aes(date, deep_sleep_prop)) + geom_line() +
          scale_x_date("%b-%Y") + xlab("Date") + ylab("Deep Sleep Proportion")
  })

  output$plot2 <- renderPlot({
    ggplot(data_df, aes(mean_rate, deep_sleep_prop)) + geom_point() +
           xlab("Mean Heart Rate") + ylab("Deep Sleep Proportion")
  })

}

shinyApp(ui, server)

