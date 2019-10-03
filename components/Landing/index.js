import React from 'react'

import { animateScroll as scroll } from 'react-scroll'

import Grid from '@material-ui/core/Grid'
import Typography from '@material-ui/core/Typography'
import { withStyles } from '@material-ui/core/styles'

import { landingStyle } from '../../styles/jss/theme.js'


import { SearchCard, StatDiv, CountsDiv, BottomLinks, WordCloud } from './Misc'
import { ChartCard, Selections } from '../Admin/dashboard.js'
import { BarChart } from '../Admin/BarChart.js'

export default withStyles(landingStyle)(class LandingPage extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      input: {},
      searchType: 'metadata',
      type: 'Overlap',
      scroll: false,
    }
  }

  scrollToTop = () => {
    scroll.scrollToTop()
  }

  searchChange = (e) => {
    this.props.searchChange(e.target.value)
  }


  render = () => {
    console.log(this.props.barcounts[this.props.ui_values.bar_chart_solo.Field_Name])
    return (
      <div>
        <Grid container
          spacing={24}
          alignItems={'center'}
          direction={'column'}>
          <Grid item xs={12} className={this.props.classes.stretched}>
            <SearchCard
              currentSearchArrayChange={this.props.currentSearchArrayChange}
              handleChange={this.props.handleChange}
              currentSearchArray={this.props.metadata_search.currentSearchArray}
              search_status={this.props.metadata_search.search_status}
              type={this.state.type}
              searchType={this.props.searchType}
              submit={this.props.submit}
              changeSignatureType={this.props.changeSignatureType}
              updateSignatureInput={this.props.updateSignatureInput}
              ui_values={this.props.ui_values}
              classes={this.props.classes}
              signature_search={this.props.signature_search}
            />
          </Grid>
          { this.props.table_counts.length === 0 ? null :
            <Grid item xs={12} className={this.props.classes.stretched}>
              <StatDiv {...this.props}/>
            </Grid>
          }
          <Grid item xs={12} className={this.props.classes.stretched}>
            <Grid container
              spacing={24}
              alignItems={'center'}>
              {
                Object.entries(this.props.pie_fields_and_stats).map(([key,value])=>(
                  <Grid item xs={12} sm>
                    <ChartCard cardheight={300} pie_stats={value.stats} resources color={'Blue'} ui_values={this.props.ui_values}/>
                    <div className={this.props.classes.centered}>
                      <Typography variant="overline">
                        Tool {value.Preferred_Name}
                      </Typography>
                    </div>
                  </Grid>
                ))
              }
              { Object.keys(this.props.barcounts).length === 0 || this.props.barcounts === undefined ? null :
                <Grid item xs={12}>
                  { this.props.ui_values.bar_chart_solo !== undefined ? (
                    <div className={this.props.classes.centered}>
                      {this.props.barcounts[this.props.ui_values.bar_chart_solo.Field_Name] !== undefined ? (
                      <BarChart meta_counts={this.props.barcounts[this.props.ui_values.bar_chart_solo.Field_Name].stats}
                        ui_values={this.props.ui_values}/>) : (
                      null
                      )}
                      <Typography variant="overline">
                        {this.props.ui_values.bar_chart_solo.Caption}
                      </Typography>
                    </div>
                  ) : (
                    <div className={this.props.classes.centered}>
                      {this.props.barcounts[Object.keys(this.props.barcounts)[0]] !== undefined ?
                      <BarChart meta_counts={this.props.barcounts[Object.keys(this.props.barcounts)[0]].stats}
                        ui_values={this.props.ui_values}/> :
                        null
                      }
                      <Typography variant="overline">
                        Bar Chart
                      </Typography>
                    </div>
                  )}
                </Grid>
              }
            </Grid>
          </Grid>
          <Grid item xs={12} className={this.props.classes.stretched}>
          </Grid>
          { Object.keys(this.props.meta_counts).length === 0 ? null :
            <Grid item xs={12} className={this.props.classes.stretched}>
              <CountsDiv {...this.props}/>
            </Grid>
          }
          { Object.keys(this.props.barcounts).length === 0 ? null :
            <Grid item xs={12} className={this.props.classes.stretched}>
              <Grid container
                spacing={24}
                alignItems={'center'}>
                <Grid item xs={12}>
                  <div className={this.props.classes.centered}>
                    <span className={this.props.classes.vertical20}>{this.props.ui_values.LandingText.text_3 || 'Examine metadata:'}</span>
                    <Selections
                      value={this.props.selected_field}
                      values={Object.keys(this.props.barcounts).filter(i=>i!==this.props.ui_values.bar_chart_solo.Field_Name).sort()}
                      onChange={(e) => this.props.handleSelectField(e)}
                    />
                  </div>
                </Grid>
                <Grid item xs md={this.props.ui_values.deactivate_wordcloud ? 12 : 6}>
                  <div className={this.props.classes.centered}>
                    <BarChart meta_counts={this.props.bar_stats}
                        ui_values={this.props.ui_values}
                    />
                    <Typography variant="overline">
                      {`Top ${this.props.bar_preferred_name}`}
                    </Typography>
                  </div>
                </Grid>
                { this.props.ui_values.deactivate_wordcloud ? null :
                  <Grid item xs md={6}>
                    <div className={this.props.classes.centered}>
                      <WordCloud classes={this.props.classes} stats={this.props.pie_stats}/>
                      <Typography variant="overline">
                        Top {this.props.pie_preferred_name} terms
                      </Typography>
                    </div>
                  </Grid>
                }
              </Grid>
            </Grid>
          }
          <Grid item xs={12}>
            <BottomLinks handleChange={this.props.handleChange}
              {...this.props} />
          </Grid>
          <Grid item xs={12}>
          </Grid>
        </Grid>
      </div>
    )
  }
})
