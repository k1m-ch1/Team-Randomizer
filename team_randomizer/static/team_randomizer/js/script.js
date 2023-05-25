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
  Object.keys(theme).forEach(colorType => {
    document.querySelectorAll(`.${colorType}-color`).forEach(element => {
      element.style.color = theme[colorType];
    });
    document.querySelectorAll(`.${colorType}-background`).forEach(element => {
      element.style.backgroundColor = theme[colorType];
    });
  })

  //toggle the radio button
  const currentCheckbox = document.querySelector(`#${currentTheme}-checkbox`)
  currentCheckbox.value = "on";
  currentCheckbox.checked = true;
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
})