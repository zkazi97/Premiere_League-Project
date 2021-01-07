#PL Dashboard
# Import packages
library(shiny)
library(plotly)
library(tidyverse)
library(readxl)
library(htmlwidgets)
library(ggplot2)
library(dplyr)
library(reshape2)
library(DT)
library(shinythemes)
theme_set(theme_grey())

# Import data
setwd("C:/Users/zaink/Downloads/TransferData")
df_team = read.csv("df_team.csv")
teams = read.csv("teams.csv")
ratings = read_excel("ratings.xlsx")
df_team2 = df_team
names(df_team2)[1] <- "Club"
names(df_team2)[3] <- "Spent (£ Millions)"
names(df_team2)[4] <- "Brought In (£ Millions)"
names(df_team2)[5] <- "Net Spending (£ Millions)"
df_team3 = melt(df_team,
                id = c("Season", "Club.Name"),
                variable.name = "Spending")

ratings2 = ratings
ratings2 = select(ratings2, -c(fee_unofficial,transfer_movement,league_name,permanent,"Top 6",standard_fee,"Rating to Fee"))
names(ratings2)[6] = "Club Involved"
names(ratings2)[9] = "Year"
names(ratings2)[10] = "Season"


ui <- fluidPage(
  titlePanel("Premiere League Transfer Dashboard"),
  theme = shinytheme('cerulean'),
  sidebarLayout(sidebarPanel(
    selectInput('Team', 'Enter Team Name', teams)
  ),
  mainPanel(tabsetPanel(
    tabPanel("Player Ratings", plotlyOutput('scatter')),
    tabPanel("Player Ratings Table", DTOutput('playerTable')),
    tabPanel("Spending Trends", plotlyOutput('trend')),
    tabPanel("Spending Table", DTOutput('table'))
    )))
)

server <- function(input, output, session) {
  output$trend <- renderPlotly({
    teamSelected = df_team %>%
      filter(Club.Name == input$Team)
    
    print(
      ggplotly(
        ggplot(teamSelected, aes(x = Season, group = 1)) +
          geom_line(aes(y = Amount.Spent, color = "Amount Spent")) +
          geom_line(aes(y = Amount.Brought.In, color = "Amount Brought In")) +
          geom_line(aes(y = Net.Spending, color = "Net Spent")) +
          geom_hline(
            yintercept = 0,
            linetype = "dashed",
            color = "black",
            size = 0.5
          ) +
          scale_colour_manual(
            "",
            breaks = c("Amount Spent", "Amount Brought In", "Net Spent"),
            values = c("steelblue", "green", "darkred")
          ) +
          theme(axis.text.x = element_text(angle = 45)) +
          labs(
            title = paste(input$Team, "Transfer Activity in 2010s"),
            y = "£ (Millions)"
          )
      )
    )
  })
  
  output$table = renderDT({
    teamSelected2 = df_team2 %>%
      filter(Club == input$Team)
  })
  
  output$scatter <- renderPlotly({
    playersSelected = ratings %>%
      filter (Club == input$Team)
      print(ggplotly( ggplot(playersSelected,tooltip = c("x","y","colour")) + 
                      geom_point(aes(x=Fee, y=Rating,color = Rating,label = Player)) +
                      labs(title = paste(input$Team, "Transfer Activity in 2010s"), x = "Fee (£ Millions)", y = "Average Rating for Club"))
        )
      }
      
  )
  
  output$playerTable = renderDT({
    playersSelected2 = ratings2 %>%
      filter(Club == input$Team)
  })
  

}

shinyApp(ui = ui, server = server)

