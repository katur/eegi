var gulp = require('gulp');
var util = require('gulp-util');
var sass = require('gulp-ruby-sass');
var coffee = require('gulp-coffee');

var sassFiles = '**/*.sass';
var sassMain = 'website/static/stylesheets/styles.sass';
var cssDir = 'website/static/stylesheets/';

var coffeeFiles = '**/*.coffee'
var jsDir = 'website/static/js/'

gulp.task('default', function() {
  gulp.watch(sassFiles, ['compileSass']);
  gulp.watch(coffeeFiles, ['compileCoffee']);
});

gulp.task('compileSass', function() {
  return sass(sassMain)
    .on('error', sass.logError)
    .pipe(gulp.dest(cssDir));
});

gulp.task('compileCoffee', function() {
  return gulp.src(coffeeFiles)
    .pipe(coffee().on('error', util.log))
    .pipe(gulp.dest(jsDir));
});
