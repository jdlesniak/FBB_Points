# FBB_Points
Fantasy baseball points projections via ZiPS
*Note: Data are not included in this repository. FanGraphs requires a membership to access these data, therefore I will not be providing the data for free.*

### Project Purpose:
Every year a few million people participate in fantasy baseball drafts. Many of them put hours of research and preparation to identify the best players, best value, and any potential deep sleepers. This project aims to help fantasy baseball GMs estimate the points their players will score with any custom league settings.

### The Data:
I purchased the ZiPS data via a subscription from FanGraphs. I used these projections as the "true" value of each player's production. Obviously, they are projections and are subject to error. Dan Szymborski does a wonderful job with his projections, you can find his 2025 introduction [here.](https://blogs.fangraphs.com/the-2025-zips-projections-are-imminent/) If you love baseball enough to care about fantasy projections, then you'll love his writing.

It is important to note that the projections are the median projection from many simulations. The median is not always the best way to describe a distribution. Consider the distribution for an imaginary player below. The x-axis shows that they have an equally likely "good" outcome and "bad" outcome, with a median that is unlikely to occur. Clearly, the median is unlikely to occur, yet, that's the chosen point. 

![BiModal](https://github.com/user-attachments/assets/e07814ac-f84f-4563-8e87-6e9583952584)

If this distribution were real, it could represent a highly-talented player that is proportionately injury-prone. If they stay healthy, then they are going to produce, but that's a big "if" for this player.

Nevertheless, all projected values will use the median observed outcome because that is Dan Szymborski's approach.

##### The One Exception
ZiPS does not provide an estimate for blown saves. I tried a few models and put in some predicted values. There are leagues that give negative points for a blown save, so I'd like to consider that in these projections. Feel free to read through that code and critique my methods if you'd like.

##### One last note on the data
I will not be providing a csv of the projections for anyone else to use. Fangraphs requires a subscription to download these projections, therefore I am not permitted to distribute them for free. Subscriptions last 30 days and are $10 as of writing this document. You are welcome to support FanGraphs and Dan Szymborski by signing up for a subscription. I think their content is worth supporting.


### Stats Considered:

##### Batters:
- tk

##### Pitchers:
- tk

