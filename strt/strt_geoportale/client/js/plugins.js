import plugins from '@mapstore/product/plugins';


const excludePlugins = [
        // framework plugins
        ContextPlugin,
        ContextCreatorPlugin,
        ContextManagerPlugin,
        Dashboard,
        DashboardEditor,
        DashboardsPlugin,
        GeoStoryPlugin,
        GeoStoriesPlugin,
        GeoStoryEditorPlugin,
        GeoStorySavePlugin,
        GeoStorySaveAsPlugin,
        DashboardSavePlugin,
        DashboardSaveAsPlugin,
        SavePlugin,
        SaveAsPlugin,
        GeoStoryNavigationPlugin,
        
        
        
        HelpPlugin,
        
        
        ManagerMenuPlugin,
        ManagerPlugin,
        MapImportPlugin,
        MapExportPlugin,
        
        
        PrintPlugin,
        
        RulesDataGridPlugin,
        RulesEditorPlugin,
        RulesManagerFooter,
        SaveStoryPlugin,
        
        SnapshotPlugin,
        
        
        ThemeSwitcherPlugin,
        
        TutorialPlugin,
        UserManagerPlugin,
        UserExtensionsPlugin,
        WidgetsBuilderPlugin,
        WidgetsPlugin,
        WidgetsTrayPlugin
]

// for (p of excludePlugins) {
//     delete plugin[p];
// }
console.log(plugins);

export default plugins;  