module.exports = function(grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        uglify: {
            options: {
                report: 'min',
                compress: {
                    dead_code: false
                }
            },
            dist: {
                files: {
                    'ui/dist/newsbuddy.min.js': ['ui/js/news_buddy.js', 'ui/js/search_controller.js', 'ui/js/stats_controller.js', 'ui/js/details_controller.js']
                }
            }
        },
        concat: {
            options: { separator: ';' },
            dist: {
                src: ['ui/js/libs/angular.min.js',
                      'ui/js/libs/typeahead.min.js',
                      'ui/js/libs/angular-*.js',
                      'ui/js/libs/bootstrap.min.js',
                      'ui/js/libs/ng-infinite-scroll.min.js',
                      'ui/dist/newsbuddy.min.js'],
                dest: 'ui/dist/nb.min.js'
            }
        },
        watch: {
            files: ['ui/js/*_controller.js'],
            tasks: ['default']
        }
    });

    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-watch');

    grunt.registerTask('default', ['uglify', 'concat']);
}
