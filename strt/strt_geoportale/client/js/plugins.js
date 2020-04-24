import plugins from '@mapstore/product/plugins';

//Rimuovo i plugins non necessari dalla configurazione
const excludePlugins = [
        // framework plugins
        "ContextPlugin",
        "ContextCreatorPlugin",
        "ContextManagerPlugin",
        "Dashboard",
        "DashboardEditor",
        "DashboardsPlugin",
        "ExamplesPlugin",
        "FeaturedMaps",
        "GeoStoryPlugin",
        "GeoStoriesPlugin",
        "GeoStoryEditorPlugin",
        "GeoStorySavePlugin",
        "GeoStorySaveAsPlugin",
        "DashboardSavePlugin",
        "DashboardSaveAsPlugin",
        "SavePlugin",
        "SaveAsPlugin",
        "GeoStoryNavigationPlugin",
        
        
        
        "HelpPlugin",
        
        
        "ManagerMenuPlugin",
        "ManagerPlugin",
        "MapImportPlugin",
        "MapExportPlugin",
        "MediaEditorPlugin",
        
        "PrintPlugin",
        
        "RulesDataGridPlugin",
        "RulesEditorPlugin",
        "RulesManagerFooter",
        "SaveStoryPlugin",
        
        "SnapshotPlugin",
        
        
        "ThemeSwitcherPlugin",
        
        "TutorialPlugin",
        "UserManagerPlugin",
        "UserExtensionsPlugin",
        "WidgetsBuilderPlugin",
        "WidgetsPlugin",
        "WidgetsTrayPlugin"
]

for (const plugin of excludePlugins) {
     delete plugins.plugins[plugin];
}
console.log(plugins);

export default plugins;  