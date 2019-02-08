jQuery(document).ready(function($) {
    if( $('div').hasClass('corporate-home') === true ) 
    {
     $('body').addClass('header-op-0');
    }

    if( $('div').hasClass('agency-home') === true ) 
    {
     $('body').addClass('header-op-2');
    }

    if( $('div').hasClass('creative-home') === true ) 
    {
     $('body').addClass('header-op-1'); // Done //
    }

    if( $('div').hasClass('modern-home') === true ) 
    {
     $('body').addClass('header-op-3'); // Done //
    }

    if( $('div').hasClass('as-animated-slider') === true ) 
    {
     $('body').addClass('header-op-4');
    }

    if( $('div').hasClass('as-home-slider02') === true ) 
    {
     $('body').addClass('header-op-5');
    }
});