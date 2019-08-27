import React from 'react'
import ChipInput from 'material-ui-chip-input'
import { withStyles } from '@material-ui/core/styles'
import Chip from '@material-ui/core/Chip'
import Tooltip from '@material-ui/core/Tooltip'
import Typography from '@material-ui/core/Typography'
import { fetchMetaData } from "../../util/redux/actions";

const styles = (theme) => ({
  info: {
    paddingTop: theme.spacing.unit * 2,
    paddingBottom: theme.spacing.unit * 2,
  },
  tooltip: {
    backgroundColor: theme.palette.common.white,
    boxShadow: theme.shadows[1],
    maxWidth: 380,
  },
})

const Info = (props) => {
  const { classes } = props
  return (
    <div className={classes.info}>
      <Typography variant="h5">
          Search operators
      </Typography>
      <ul>
        <li>
          <div>
            <Typography variant="h6">
                Exclude word from search
            </Typography>
            <Typography variant="body2">
              {'Prefix query with "-" or "!", e.g.'} &nbsp;
            </Typography>
            <Typography variant="overline" gutterBottom>
              <Chip
                label={'Imatinib'}
                onDelete={() => {}}
              /> -Stat3
            </Typography>
          </div>
        </li>
        <li>
          <div>
            <Typography variant="h6">
                Combine searches
            </Typography>
            <Typography variant="body2">
              {'Prefix query "or " or "|", e.g.'} &nbsp;
            </Typography>
            <Typography variant="overline" gutterBottom>
              <Chip
                label={'Imatinib'}
                onDelete={() => {}}
              /> or Stat3
            </Typography>
          </div>
        </li>
        <li>
          <div>
            <Typography variant="h6">
                Search for specific field
            </Typography>
            <Typography variant="body2">
              {'Prefix query with "[desired_field]:", e.g.'}
            </Typography>
            <Typography variant="overline" gutterBottom>
              <Chip
                label={'Disease: neuropathy'}
                onDelete={() => {}}
              /> {'PMID: 12345'}
            </Typography>
          </div>
        </li>
      </ul>
    </div>
  )
}

class MetadataSearchBox extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      search: [],
    }
    this.performSearch = this.performSearch.bind(this);
  }

  performSearch(search) {
    this.props.fetchMetaData({ search });
    this.setState({
      search
    })
  }

  renderChips = (
      {
        value,
        isDisabled,
        className,
      },
      key
  ) => {
    let backgroundColor = '#e0e0e0'
    const fontColor = '#000'
    let icon = 'mdi-code-equal' // mdi-code-not-equal
    let chip_value = value
    // if (value.startsWith("|!") || value.startsWith("!|")){
    //   // or not
    //   icon = "mdi-code-not-equal"
    //   chip_value = value.substring(2)
    //   backgroundColor = "#9e9e9e"
    //   fontColor = "#FFF"
    // } else if (value.startsWith("|")){
    //   // or
    //   chip_value = value.substring(1)
    //   backgroundColor = "#9e9e9e"
    //   fontColor = "#FFF"
    // } else
    if (value.startsWith('!') || value.startsWith('-')) {
      // not
      icon = 'mdi-code-not-equal'
      backgroundColor = '#FFBABA'
      chip_value = value.substring(1)
    } else if (value.toLowerCase().startsWith('or ')) {
      // or
      icon = 'mdi-equal-box mdi-rotate-90'
      backgroundColor = '#FFEAD9'
      chip_value = value.substring(3)
    } else if (value.startsWith('|')) {
      // or
      icon = 'mdi-equal-box mdi-rotate-90'
      backgroundColor = '#FFEAD9'
      chip_value = value.substring(1)
    }
    return (
      <Chip
        key={key}
        avatar={<span className={`mdi ${icon} mdi-24px`}/>}
        label={chip_value}
        onDelete={() => {
          const search = this.state.search.filter((term) => term != value)
          this.performSearch(search)
        }}
        style={{
          pointerEvents: isDisabled ? 'none' : undefined,
          backgroundColor: backgroundColor,
          color: fontColor,
        }}
        className={className}
      />
    )
  }

  render() {
    const examples = this.props.ui_values.LandingText.search_terms
    const { classes } = this.props
    return (
      <form action="javascript:void(0);">
        <div className="input-field">
          <span className="mdi mdi-magnify mdi-36px"></span>
          <ChipInput
            placeholder={this.state.search.length > 0 ? 'Add filter' :
                this.props.ui_values.LandingText.metadata_placeholder}
            value={this.state.search}
            chipRenderer={this.renderChips}
            disableUnderline
            alwaysShowPlaceholder
            InputProps={{
              inputProps: {
                style: {
                  border: 'none',
                },
              },
            }}
            style={{
              fontWeight: 500,
              color: 'rgba(0, 0, 0, 0.54)',
              borderRadius: '2px',
              border: 0,
              minheight: '35px',
              marginBottom: 0,
              width: '430px',
              padding: this.state.search.length === 0 ? '8px 8px 0 60px' : '8px 8px 0 8px',
              background: '#f7f7f7',
            }}
            onAdd={(chip) => {
              const search = [...this.state.search, chip]
              this.performSearch(search)
            }}
            onDelete={(chip, index) => {
              const search = this.state.search.filter((term) => term != chip)
              this.performSearch(search)
            }}
            blurBehavior="add"
          />
          <span>&nbsp;&nbsp;</span>
          <button className="btn waves-effect waves-light" type="submit" name="action"
            style={{ marginBottom: 20 }}
            onClick={() =>
              this.performSearch(this.state.search)
            }
          >
          { ["Initializing", "Matched"].indexOf(this.props.search_status) > -1 ? 
            <React.Fragment>
              Searching
              <i className="mdi mdi-spin mdi-loading right" />
            </React.Fragment>: 
            <React.Fragment>
              Search
              <i className="material-icons right">send</i>
            </React.Fragment>
          }
          </button>
        </div>
        {examples.map((example) => (
          <a
            key={example}
            className="chip grey white-text waves-effect waves-light"

            onClick={() => this.performSearch([example])}
          >
            {example}
          </a>
        ))}
        <Tooltip title={<Info {...this.props}/>} interactive placement="right-start" classes={{ tooltip: classes.tooltip }}>
          <span className="mdi mdi-information mdi-18px" />
        </Tooltip>
      </form>
    )
  }
}

export default withStyles(styles)(MetadataSearchBox)
