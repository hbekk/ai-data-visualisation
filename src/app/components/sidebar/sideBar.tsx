import Logo from "./Logo";
import '../../styles/Sidebar/sidebar.css';
import ArchivedCharts from "./archived_charts";
import ChartHistory from "./chart_history";

const SideBar: React.FC = () => {
  return (
    <>
      <Logo />
      <div className="sidebar-list-container">
        <ChartHistory />
        <div className="divider"></div>
        <ArchivedCharts />
      </div>
    </>
  );
};

export default SideBar;
