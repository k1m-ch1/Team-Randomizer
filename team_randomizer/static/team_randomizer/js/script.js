const RANDOMIZER_THEME = 'randomizerTheme';
const THEME = {
  "light":{
    primary: "#060208",
    secondary: "#ebd5f6 ",
    primaryButton: "#5a1a7a",
    secondaryButton: "#f1e2f9 ",
    accent: "#691e8f"
  },
  "dark":{
    primary: "#f6f8f1",
    secondary: "#1b1f0f",
    primaryButton: "#7360af",
    secondaryButton: "#12140a",
    accent: "#463870"
  }
}

const DEFAULT_THEME = Object.keys(THEME)[0];

function setThemeAndRender(themeToSet=null){
  console.log(themeToSet);

  // check for prev state and set to default if no saved state
  const prevThemeState = localStorage.getItem(RANDOMIZER_THEME);
  if (prevThemeState === null || !prevThemeState in THEME){
    localStorage.setItem(RANDOMIZER_THEME, DEFAULT_THEME);
  }

  // optional set theme
  if (themeToSet in THEME){
    localStorage.setItem(RANDOMIZER_THEME, themeToSet);
  }
  

  const currentTheme = localStorage.getItem(RANDOMIZER_THEME)
  // set the class name equals to colors
  const theme = THEME[currentTheme];
  let baseThemeForCss = '';
  let colorForCss = '';
  let backgroundColorForCss = '';
  let alphaColorForCss = '';
  let alphaBackgroundColorForCss = '';
  Object.keys(theme).forEach(colorType => {
    baseThemeForCss += `--${colorType}: ${theme[colorType]};`;
    colorForCss += 
    `.${colorType}-color{
      color: ${theme[colorType]}
    }\n`;

    backgroundColorForCss += 
    `.${colorType}-background {
      background-color: ${theme[colorType]};
    }\n`;

    //setting every alpha value for every color
    for(let i = 0; i <= 0xFF; i++){
      let alphaValue = i.toString(16).toUpperCase()
      alphaColorForCss += 
      `.${colorType}-color-${alphaValue} {
        color: ${theme[colorType]+alphaValue};
      }\n`;
      alphaBackgroundColorForCss += 
      `.${colorType}-background-${alphaValue} {
        background-color: ${theme[colorType]+alphaValue};
      }\n`
    }
  })
  
  
  //toggle the radio button
  const currentCheckbox = document.querySelector(`#${currentTheme}-checkbox`)
  currentCheckbox.value = "on";
  currentCheckbox.checked = true;
  
  //loading css
  document.querySelector('head').innerHTML += 
  `<style>
  :root {
    ${baseThemeForCss}
  }
    ${colorForCss}
    ${backgroundColorForCss}
    ${alphaColorForCss}
    ${alphaBackgroundColorForCss}
    </style>`;
  console.log('loaded the css!');
}


document.addEventListener('DOMContentLoaded', function(){
  setThemeAndRender();

  // Check for theme switch
  Object.keys(THEME).forEach(theme => {
    document.querySelector(`#${theme}-checkbox`).onchange = function(){
      if (this.value === "on"){
        setThemeAndRender(theme);
      }
    }
  })

  // Hide message block
  message_div = document.querySelector('#message') 
  if(message_div != null){
    setTimeout(() => {
      message_div.style.display = 'none';
    },5000)
  }

})