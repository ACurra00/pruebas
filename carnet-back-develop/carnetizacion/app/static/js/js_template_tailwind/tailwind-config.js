tailwind.config = {
    theme: {
        screens: {
          'xs': '320px',
          // => @media (min-width: 320px) { ... }
    
          'sm': '576px',
          // => @media (min-width: 576px) { ... }
    
          'md': '768px',
          // => @media (min-width: 768px) { ... }
    
          'lg': '992px',
          // => @media (min-width: 992px) { ... }
    
          'xl': '1201px',
          // => @media (min-width: 1200px) { ... }
    
          'xxl': '1401px',
          // => @media (min-width: 1400px) { ... }
    
          'xxxl': '1601px',
          // => @media (min-width: 1601px) { ... }
    
          'maxDesktop': {'max': '1800px'},
          // => @media (max-width: 1700px) { ... }
    
          'max2Xl': {'max': '1600px'},
          // => @media (max-width: 1600px) { ... }
    
          'maxXl': {'max': '1400px'},
          // => @media (max-width: 1200px) { ... }
    
          'maxLg': {'max': '1200px'},
          // => @media (max-width: 1200px) { ... }
    
          'maxMd': {'max': '991px'},
          // => @media (max-width: 991px) { ... }
    
          'maxSm': {'max': '767px'},
          // => @media (max-width: 767px) { ... }
    
          'maxXs': {'max': '575px'},
          // => @media (max-width: 575px) { ... }
    
    
          'minMaxDesktop': {'min': '1601px', 'max': '1800px'},
          // => @media (min-width: 1601px) and (max-width: 1800px) { ... }
    
          'minMaxLaptop': {'min': '1401px', 'max': '1600px'},
          // => @media (min-width: 1401px) and (max-width: 1600px) { ... }
    
          'minMaxTablet': {'min': '1201px', 'max': '1400px'},
          // => @media (min-width: 1201px) and (max-width: 1400px) { ... }
    
          'minMaxTab': {'min': '992px', 'max': '1200px'},
          // => @media (min-width: 992px) and (max-width: 1200px) { ... }
    
          'minMaxTabSmall': {'min': '768px', 'max': '991px'},
          // => @media (min-width: 768px) and (max-width: 991px) { ... }
    
          'minMaxMobile': {'min': '576px', 'max': '767px'},
          // => @media (min-width: 576px) and (max-width: 576px) { ... }
        },
        container: {
          center: true,
          padding: '15px',
        },
        fontFamily: {
          'primary': ["'Nunito Sans', sans-serif"],
          'fontawesome': ["Font Awesome 5 Pro"],
        },
        extend: {
          colors: {
            'white': '#ffffff',
            'heading': '#0D0F19',
            'themeBlue': '#6F4EF6',
            'themeGreen': '#5BC5A8',
            'themeGreenDark': '#27DB8D',
            'themeOrange': '#FF9720',
            'themeOrangeDark': '#FFC403',
            'themeWarn': '#DF7272',
            'themePerple': '#866AD4',
            'black': '#000',
            'bodyText': '#616161',
            'grayBorder': '#EFF0F2',
            'bodyBg': '#F6F6F6',
            'grayBg': '#FCFCFC',
            'grayBgLight': '#f9f9f9',
          },
        },
    }
}