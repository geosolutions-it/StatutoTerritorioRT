/*
 * Copyright 2020, GeoSolutions Sas.
 * All rights reserved.
 *
 * This source code is licensed under the BSD-style license found in the
 * LICENSE file in the root directory of this source tree.
*/

import History from '@mapstore/plugins/History';

// import AboutPlugin from '@mapstore/product/plugins/About';
import AttributionPlugin from '@mapstore/product/plugins/Attribution';
// import ExamplesPlugin from '@mapstore/product/plugins/Examples';
// import FooterPlugin from '@mapstore/product/plugins/Footer';
import ForkPlugin from '@mapstore/product/plugins/Fork';
import HeaderPlugin from '@mapstore/product/plugins/Header';
import HomeDescriptionPlugin from '@mapstore/product/plugins/HomeDescription';
import MadeWithLovePlugin from '@mapstore/product/plugins/MadeWithLove';
import MailingListsPlugin from '@mapstore/product/plugins/MailingLists';
import MapTypePlugin from '@mapstore/product/plugins/MapType';
import NavMenu from '@mapstore/product/plugins/NavMenu';
// framework plugins
import AddGroupPlugin from '@mapstore/plugins/AddGroup';
// import AnnotationsPlugin from '@mapstore/plugins/Annotations';
import AutoMapUpdatePlugin from '@mapstore/plugins/AutoMapUpdate';
import BackgroundSelectorPlugin from '@mapstore/plugins/BackgroundSelector';
// import BackgroundSwitcherPlugin from '@mapstore/plugins/BackgroundSwitcher';
import BurgerMenuPlugin from '@mapstore/plugins/BurgerMenu';
import CRSSelectorPlugin from '@mapstore/plugins/CRSSelector';
import ContentTabs from '@mapstore/plugins/ContentTabs';
// import ContextPlugin from '@mapstore/plugins/Context';
// import ContextCreatorPlugin from '@mapstore/plugins/ContextCreator';
// import ContextManagerPlugin from '@mapstore/plugins/contextmanager/ContextManager';
import CookiePlugin from '@mapstore/plugins/Cookie';
// import CreateNewMapPlugin from '@mapstore/plugins/CreateNewMap';
// import Dashboard from '@mapstore/plugins/Dashboard';
// import DashboardEditor from '@mapstore/plugins/DashboardEditor';
// import DashboardsPlugin from '@mapstore/plugins/Dashboards';
import DetailsPlugin from '@mapstore/plugins/Details';
import DrawerMenuPlugin from '@mapstore/plugins/DrawerMenu';
import ExpanderPlugin from '@mapstore/plugins/Expander';
import FeatureEditorPlugin from '@mapstore/plugins/FeatureEditor';
// import FeaturedMaps from '@mapstore/plugins/FeaturedMaps';
import FeedbackMaskPlugin from '@mapstore/plugins/FeedbackMask';
import FilterLayerPlugin from '@mapstore/plugins/FilterLayer';
import FloatingLegendPlugin from '@mapstore/plugins/FloatingLegend';
import FullScreenPlugin from '@mapstore/plugins/FullScreen';
// import GeoStoryPlugin from '@mapstore/plugins/GeoStory';
// import GeoStoriesPlugin from '@mapstore/plugins/GeoStories';
// import GeoStoryEditorPlugin from '@mapstore/plugins/GeoStoryEditor';
// import GeoStorySavePlugin from '@mapstore/plugins/GeoStorySave';
// import GeoStorySaveAsPlugin from '@mapstore/plugins/GeoStorySave';
// import DashboardSavePlugin from '@mapstore/plugins/DashboardSave';
// import DashboardSaveAsPlugin from '@mapstore/plugins/DashboardSave';
// import GeoStoryNavigationPlugin from '@mapstore/plugins/GeoStoryNavigation';
// import GlobeViewSwitcherPlugin from '@mapstore/plugins/GlobeViewSwitcher';
import GoFull from '@mapstore/plugins/GoFull';
import GridContainerPlugin from '@mapstore/plugins/GridContainer';
import GroupManagerPlugin from '@mapstore/plugins/manager/GroupManager';
// import HelpLinkPlugin from '@mapstore/plugins/HelpLink';
// import HelpPlugin from '@mapstore/plugins/Help';
// import HomePlugin from '@mapstore/plugins/Home';
import IdentifyPlugin from '@mapstore/plugins/Identify';
import LanguagePlugin from '@mapstore/plugins/Language';
// import LocatePlugin from '@mapstore/plugins/Locate';
import LoginPlugin from '@mapstore/plugins/Login';
// import ManagerMenuPlugin from '@mapstore/plugins/manager/ManagerMenu';
// import ManagerPlugin from '@mapstore/plugins/manager/Manager';
import MapEditorPlugin from '@mapstore/plugins/MapEditor';
// import MapExportPlugin from '@mapstore/plugins/MapExport';
import MapFooterPlugin from '@mapstore/plugins/MapFooter';
import MapImportPlugin from '@mapstore/plugins/MapImport';
import MapLoadingPlugin from '@mapstore/plugins/MapLoading';
import MapPlugin from '@mapstore/plugins/Map';
import MapSearchPlugin from '@mapstore/plugins/MapSearch';
// import MapsPlugin from '@mapstore/plugins/Maps';
import MapCatalogPlugin from '@mapstore/plugins/MapCatalog';
import MapTemplatesPlugin from '@mapstore/plugins/MapTemplates';
import MeasurePlugin from '@mapstore/plugins/Measure';
// import MediaEditorPlugin from '@mapstore/plugins/MediaEditor';
import MetadataExplorerPlugin from '@mapstore/plugins/MetadataExplorer';
import MousePositionPlugin from '@mapstore/plugins/MousePosition';
import NotificationsPlugin from '@mapstore/plugins/Notifications';
import OmniBarPlugin from '@mapstore/plugins/OmniBar';
import PlaybackPlugin from '@mapstore/plugins/Playback.jsx';
import PrintPlugin from '@mapstore/plugins/Print';
import QueryPanelPlugin from '@mapstore/plugins/QueryPanel';
import RedirectPlugin from '@mapstore/plugins/Redirect';
const RedoPlugin = History;
// import RulesDataGridPlugin from '@mapstore/plugins/RulesDataGrid';
// import RulesEditorPlugin from '@mapstore/plugins/RulesEditor';
// import RulesManagerFooter from '@mapstore/plugins/RulesManagerFooter';
import SavePlugin from '@mapstore/plugins/Save';
import SaveAsPlugin from '@mapstore/plugins/SaveAs';
// import SaveStoryPlugin from '@mapstore/plugins/GeoStorySave';
import ScaleBoxPlugin from '@mapstore/plugins/ScaleBox';
import ScrollTopPlugin from '@mapstore/plugins/ScrollTop';
import SearchPlugin from '@mapstore/plugins/Search';
import SearchServicesConfigPlugin from '@mapstore/plugins/SearchServicesConfig';
import SettingsPlugin from '@mapstore/plugins/Settings';
import SharePlugin from '@js/plugins/Share';
// import SnapshotPlugin from '@mapstore/plugins/Snapshot';
import StyleEditorPlugin from '@mapstore/plugins/StyleEditor';
import TOCItemsSettingsPlugin from '@mapstore/plugins/TOCItemsSettings';
import ThematicLayerPlugin from '@mapstore/plugins/ThematicLayer';
// import ThemeSwitcherPlugin from '@mapstore/plugins/ThemeSwitcher';
import TimelinePlugin from '@mapstore/plugins/Timeline';
import ToolbarPlugin from '@mapstore/plugins/Toolbar';
// import TutorialPlugin from '@mapstore/plugins/Tutorial';
const UndoPlugin = History;
// import UserManagerPlugin from '@mapstore/plugins/manager/UserManager';
// import UserExtensionsPlugin from '@mapstore/plugins/UserExtensions';
import VersionPlugin from '@mapstore/plugins/Version';
import LayerDownloadPlugin from '@mapstore/plugins/LayerDownload';
import WidgetsBuilderPlugin from '@mapstore/plugins/WidgetsBuilder';
import WidgetsPlugin from '@mapstore/plugins/Widgets';
import WidgetsTrayPlugin from '@mapstore/plugins/WidgetsTray';
import ZoomAllPlugin from '@mapstore/plugins/ZoomAll';
import ZoomInPlugin from '@mapstore/plugins/ZoomIn';
import ZoomOutPlugin from '@mapstore/plugins/ZoomOut';

import ReactSwipe from 'react-swipeable-views';
import SwipeHeader from '@mapstore/components/data/identify/SwipeHeader';

// custom
import HomeCatalogPlugin from '@js/plugins/HomeCatalog';
import SerapideCatalogPlugin from '@js/plugins/SerapideCatalog';
import TOCPlugin from '@js/plugins/TOC';

export const plugins = {
    // AboutPlugin,
    AttributionPlugin,
    ForkPlugin,
    HeaderPlugin,
    HomeDescriptionPlugin,
    MadeWithLovePlugin,
    MailingListsPlugin,
    MapTypePlugin,
    NavMenu,
    // framework plugins
    AddGroupPlugin,
    // AnnotationsPlugin,
    AutoMapUpdatePlugin,
    BackgroundSelectorPlugin,
    // BackgroundSwitcherPlugin,
    BurgerMenuPlugin,
    CRSSelectorPlugin,
    ContentTabs,
    CookiePlugin,
    // CreateNewMapPlugin,
    DetailsPlugin,
    DrawerMenuPlugin,
    ExpanderPlugin,
    FeatureEditorPlugin,
    FeedbackMaskPlugin,
    FilterLayerPlugin,
    FloatingLegendPlugin,
    FullScreenPlugin,
    // GlobeViewSwitcherPlugin,
    GoFull,
    GridContainerPlugin,
    GroupManagerPlugin,
    // HelpLinkPlugin,
    // HomePlugin,
    IdentifyPlugin,
    LanguagePlugin,
    // LocatePlugin,
    LoginPlugin,
    MapEditorPlugin,
    MapFooterPlugin,
    MapImportPlugin,
    MapLoadingPlugin,
    MapPlugin,
    MapSearchPlugin,
    // MapsPlugin,
    MapCatalogPlugin,
    MapTemplatesPlugin,
    MeasurePlugin,
    MetadataExplorerPlugin,
    MousePositionPlugin,
    NotificationsPlugin,
    OmniBarPlugin,
    PlaybackPlugin,
    PrintPlugin,
    QueryPanelPlugin,
    RedirectPlugin,
    RedoPlugin,
    SavePlugin,
    SaveAsPlugin,
    ScaleBoxPlugin,
    ScrollTopPlugin,
    SearchPlugin,
    SearchServicesConfigPlugin,
    SettingsPlugin,
    SharePlugin,
    StyleEditorPlugin,
    TOCItemsSettingsPlugin,
    TOCPlugin,
    ThematicLayerPlugin,
    TimelinePlugin,
    ToolbarPlugin,
    UndoPlugin,
    VersionPlugin,
    LayerDownloadPlugin,
    ZoomAllPlugin,
    ZoomInPlugin,
    ZoomOutPlugin,

    WidgetsBuilderPlugin,
    WidgetsPlugin,
    WidgetsTrayPlugin,

    // custom
    HomeCatalogPlugin,
    SerapideCatalogPlugin
};

export const requires = {
    ReactSwipe,
    SwipeHeader
};

export default {
    plugins,
    requires
};
