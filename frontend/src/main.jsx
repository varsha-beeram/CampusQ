import React,{useEffect,useState} from "react";
import {createRoot} from "react-dom/client";
import {BrowserRouter,useLocation,useNavigate,Link,Routes,Route,Navigate} from "react-router-dom";
import axios from "axios";
import "./style.css";

const API=import.meta.env.VITE_API_URL||"http://localhost:5000/api";
const api=axios.create({baseURL:API});
api.interceptors.request.use(c=>{const t=localStorage.getItem("campusq_token");if(t)c.headers.Authorization=`Bearer ${t}`;return c});
const user=()=>{try{return JSON.parse(localStorage.getItem("campusq_user"))}catch{return null}};
const logout=()=>{localStorage.clear();location.href="/login"};

const icons={
  grid:"M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z",
  service:"M4 6h16M7 3v6M17 3v6M5 10h14v9H5z",
  ticket:"M5 4h14v16H5zM8 8h8M8 12h8M8 16h5",
  clock:"M12 7v5l3 2M21 12a9 9 0 11-18 0 9 9 0 0118 0",
  users:"M16 21v-2a4 4 0 00-4-4H7a4 4 0 00-4 4v2M9.5 11a4 4 0 100-8 4 4 0 000 8M17 11a4 4 0 100-8",
  bell:"M18 8a6 6 0 00-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M10 21h4",
  arrow:"M5 12h14M13 6l6 6-6 6",
  check:"M5 12l4 4L19 6",
  x:"M6 6l12 12M18 6L6 18"
};
function Icon({n}){return <svg className="ico" viewBox="0 0 24 24"><path d={icons[n]||icons.grid}/></svg>}

function Shell({children}){
 const u=user(),loc=useLocation();
 const links=u?.role==="STUDENT"?[
  ["/","Overview","grid"],["/services","Find a service","service"],["/token","My queue","ticket"],["/history","History","clock"]
 ]:u?.role==="STAFF"?[[ "/staff","Queue desk","ticket"],["/","Overview","grid"]]:[[ "/admin","Overview","grid"],["/admin/users","Users","users"]];
 return <div className="shell"><aside className="side">
  <Link to="/" className="brand"><span className="brand-box">C</span>Campus<span>Q</span></Link>
  <div className="portal">{u?.role} PORTAL</div>
  <nav>{links.map(([p,t,i])=><Link className={loc.pathname===p?"nav active":"nav"} to={p} key={p}><Icon n={i}/>{t}</Link>)}</nav>
  <div className="side-bottom"><div className="side-tip"><b>Smart campus services</b><span>Less waiting. More doing.</span></div><button className="signout" onClick={logout}>Sign out</button></div>
 </aside><main className="main"><header className="top"><div className="mobile-brand">Campus<span>Q</span></div><div className="profile"><div className="avatar">{(u?.name||"U")[0]}</div><div><b>{u?.name}</b><small>{u?.role}</small></div></div></header>{children}</main></div>
}

function Guard({roles,children}){if(!localStorage.getItem("campusq_token"))return <Navigate to="/login"/>;if(roles&&!roles.includes(user()?.role))return <Navigate to="/"/>;return <Shell>{children}</Shell>}

function Auth({children,title,sub}){
 return <div className="auth"><div className="auth-left"><div className="auth-brand">Campus<span>Q</span></div><div><div className="eyebrow light">SMART CAMPUS QUEUE</div><h1>Don't wait.<br/><span>Know your turn.</span></h1><p>Digital queue management for modern campus services.</p></div><small>CampusQ · Final-year project</small></div><div className="auth-right"><div className="auth-card"><div className="auth-brand dark">Campus<span>Q</span></div><h2>{title}</h2><p className="sub">{sub}</p>{children}</div></div></div>
}
function Login(){
 const nav=useNavigate(),[email,setEmail]=useState("student@campusq.com"),[password,setPassword]=useState("Student@123"),[err,setErr]=useState("");
 async function go(e){e.preventDefault();try{const r=await api.post("/auth/login",{email,password});localStorage.setItem("campusq_token",r.data.data.token);localStorage.setItem("campusq_user",JSON.stringify(r.data.data.user));nav("/")}catch(e){setErr(e.response?.data?.message||"Sign in failed")}}
 return <Auth title="Welcome back" sub="Sign in to manage your campus queue."><form className="form" onSubmit={go}><label>Email<input type="email" value={email} onChange={e=>setEmail(e.target.value)}/></label><label>Password<input type="password" value={password} onChange={e=>setPassword(e.target.value)}/></label>{err&&<div className="err">{err}</div>}<button className="btn primary full">Sign in</button></form><div className="demo"><b>Demo student</b><span>student@campusq.com · Student@123</span></div><p className="switch">New to CampusQ? <Link to="/register">Create account</Link></p></Auth>
}
function Register(){
 const nav=useNavigate(),[f,setF]=useState({name:"",email:"",phone:"",password:""}),[err,setErr]=useState("");
 async function go(e){e.preventDefault();try{const r=await api.post("/auth/register",f);localStorage.setItem("campusq_token",r.data.data.token);localStorage.setItem("campusq_user",JSON.stringify(r.data.data.user));nav("/")}catch(e){setErr(e.response?.data?.message||"Registration failed")}}
 return <Auth title="Create account" sub="Start using CampusQ today."><form className="form" onSubmit={go}><label>Full name<input required value={f.name} onChange={e=>setF({...f,name:e.target.value})}/></label><label>Email<input required type="email" value={f.email} onChange={e=>setF({...f,email:e.target.value})}/></label><label>Phone <small>optional</small><input value={f.phone} onChange={e=>setF({...f,phone:e.target.value})}/></label><label>Password<input required minLength="8" type="password" value={f.password} onChange={e=>setF({...f,password:e.target.value})}/></label>{err&&<div className="err">{err}</div>}<button className="btn primary full">Create account</button></form><p className="switch">Already registered? <Link to="/login">Sign in</Link></p></Auth>
}

function Heading({eyebrow,title,desc}){return <div className="heading"><div><div className="eyebrow">{eyebrow}</div><h1>{title}</h1>{desc&&<p>{desc}</p>}</div></div>}
function Stat({icon,label,value,sub}){return <div className="stat"><div className="stat-ico"><Icon n={icon}/></div><div><small>{label}</small><strong>{value}</strong><span>{sub}</span></div></div>}

function StudentHome(){
 const u=user(),[active,setActive]=useState([]);
 useEffect(()=>{api.get("/tokens/my-active").then(r=>setActive(r.data.data)).catch(()=>{})},[]);
 const t=active[0];
 return <Guard roles={["STUDENT"]}><Heading eyebrow="STUDENT PORTAL" title={`Good afternoon, ${u?.name?.split(" ")[0]||"there"}.`} desc="Manage your campus visits without standing in line."/>
 {t?<div className="live-hero"><div><div className="eyebrow light">ACTIVE QUEUE · {t.service_name}</div><div className="hero-token">{t.display_token}</div><p className="hero-status"><i/> {t.status==="WAITING"?"Queue is moving":t.status==="CALLED"?"Your turn is now":"Service in progress"}</p><Link className="btn light-btn" to="/token">Track my queue <Icon n="arrow"/></Link></div><div className="hero-metrics"><div><small>PEOPLE AHEAD</small><b>{t.people_ahead}</b></div><div><small>EST. WAIT</small><b>{t.estimated_wait_minutes}<em> min</em></b></div><div><small>EXPECTED</small><b>{t.expected_turn?new Date(t.expected_turn).toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"}):"—"}</b></div></div></div>
 :<div className="welcome-hero"><div><div className="eyebrow light">CAMPUSQ</div><h2>Skip the line.<br/><span>Keep your time.</span></h2><p>Join a campus service queue from your phone and know exactly when your turn is approaching.</p><Link className="btn light-btn" to="/services">Find a service <Icon n="arrow"/></Link></div><div className="hero-visual"><div className="mock-ticket"><small>NOW SERVING</small><b>A-018</b><span>Academic Services · Counter 1</span></div><div className="mock-ticket back"><small>NEXT UP</small><b>A-019</b><span>Queue is moving</span></div></div></div>}
 <div className="stats"><Stat icon="clock" label="Current wait" value={t?`${t.estimated_wait_minutes} min`:"—"} sub={t?"Estimated":"No active queue"}/><Stat icon="ticket" label="Active token" value={t?t.display_token:"—"} sub={t?t.status:"Join a service"}/><Stat icon="service" label="Services" value="5" sub="Available today"/></div>
 <div className="two"><div className="panel"><div className="panel-title"><div><h3>How CampusQ works</h3><p>Three steps from queue to counter.</p></div></div><div className="steps"><div><b>01</b><strong>Choose</strong><span>Select a campus service.</span></div><div><b>02</b><strong>Join</strong><span>Get a digital token.</span></div><div><b>03</b><strong>Arrive</strong><span>Come when your turn is near.</span></div></div></div><div className="panel mint"><div className="eyebrow">SMART QUEUE</div><h3>Know before you go.</h3><p>CampusQ estimates your wait using the live queue and average service time.</p><Link to="/services">Explore services →</Link></div></div></Guard>
}

function Services(){
  const [deps, setDeps] = useState([]);
  const [sel, setSel] = useState(null);
  const [services, setServices] = useState([]);
  const [toast, setToast] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDepartments() {
      try {
        setLoading(true);
        setError("");

        const response = await api.get("/departments");

        console.log("CampusQ departments:", response.data);

        const departments = response.data?.data || [];
        setDeps(departments);
      } catch (err) {
        console.error("Failed to load departments:", err);
        setError(
          err.response?.data?.message ||
          "Unable to load departments. Please make sure the Flask backend is running."
        );
      } finally {
        setLoading(false);
      }
    }

    loadDepartments();
  }, []);

  async function choose(d) {
    try {
      setSel(d);
      setServices([]);
      setError("");

      const response = await api.get(
        `/departments/${d.id}/sub-departments`
      );

      const subs = response.data?.data || [];

      let all = [];

      for (const sub of subs) {
        const serviceResponse = await api.get(
          `/sub-departments/${sub.id}/services`
        );

        all.push(...(serviceResponse.data?.data || []));
      }

      setServices(all);
    } catch (err) {
      console.error("Failed to load services:", err);
      setServices([]);
      setError(
        err.response?.data?.message ||
        "Unable to load services for this department."
      );
    }
  }

 async function join(s) {
  try {
    const r = await api.post("/tokens/join", {
      service_id: s.id
    });

    console.log("JOIN QUEUE SUCCESS:", r.data);

    setToast(
      `Queue joined — your token is ${r.data.data.display_token}`
    );
  } catch (e) {
    console.error("JOIN QUEUE ERROR:", e.response?.data || e);

    setToast(
      e.response?.data?.message ||
      e.response?.data?.error ||
      `Join queue failed (${e.response?.status || "unknown error"})`
    );
  }
}

  return (
    <Guard roles={["STUDENT"]}>
      <Heading
        eyebrow="SERVICES"
        title="Find a campus service"
        desc="Choose a department, view its live service options and join a queue."
      />

      {error && (
        <div className="err" style={{ marginBottom: "20px" }}>
          {error}
        </div>
      )}

      <div className="service-layout">

        <div className="departments">

          {loading ? (
            <div className="empty small">
              Loading departments...
            </div>
          ) : deps.length === 0 ? (
            <div className="empty small">
              No departments available.
            </div>
          ) : (
            deps.map((d, i) => (
              <button
                className={
                  sel?.id === d.id
                    ? "dept selected"
                    : "dept"
                }
                key={d.id}
                onClick={() => choose(d)}
              >
                <span className="num">
                  {String(i + 1).padStart(2, "0")}
                </span>

                <span>
                  <b>{d.name}</b>
                  <small>
                    {d.description || "Campus service department"}
                  </small>
                </span>

                <span>→</span>
              </button>
            ))
          )}

        </div>

        <div className="service-list">

          {sel ? (
            <>
              <div className="list-head">
                <div>
                  <div className="eyebrow">
                    AVAILABLE TODAY
                  </div>

                  <h2>{sel.name}</h2>
                </div>

                <span>
                  {services.length} services
                </span>
              </div>

              {services.length === 0 ? (
                <div className="choose">
                  <div className="choose-icon">
                    <Icon n="service" />
                  </div>

                  <h2>No services available</h2>

                  <p>
                    There are no services available for this
                    department right now.
                  </p>
                </div>
              ) : (
                services.map((s) => (
                  <div className="service" key={s.id}>

                    <div className="service-icon">
                      <Icon n="service" />
                    </div>

                    <div className="service-main">
                      <h3>{s.name}</h3>

                      <p>
                        {s.description}
                      </p>

                      <div className="service-meta">
                        <span>Avg. service time</span>

                        <b>
                          ~{s.average_service_time} min
                        </b>

                        <span className="dot">
                          •
                        </span>

                        <span>
                          Queue live
                        </span>
                      </div>
                    </div>

                    <button
                      className="btn primary"
                      onClick={() => join(s)}
                    >
                      Join queue
                    </button>

                  </div>
                ))
              )}
            </>
          ) : (
            <div className="choose">

              <div className="choose-icon">
                <Icon n="service" />
              </div>

              <h2>
                Select a department
              </h2>

              <p>
                Pick a department on the left to see its services.
              </p>

            </div>
          )}

        </div>

      </div>

      {toast && (
        <div className="toast">
          {toast}

          <button onClick={() => setToast("")}>
            ×
          </button>
        </div>
      )}

    </Guard>
  );

}

function Token(){
 const [t,setT]=useState(null),[msg,setMsg]=useState("");
 async function load(){try{const r=await api.get("/tokens/my-active");setT(r.data.data[0]||null)}catch{}}
 useEffect(()=>{load();const i=setInterval(load,3000);return()=>clearInterval(i)},[]);
 async function cancel(){if(!t)return;try{await api.post(`/tokens/${t.id}/cancel`);setMsg("Your token was cancelled.");load()}catch(e){setMsg(e.response?.data?.message||"Unable to cancel")}}
 return <Guard roles={["STUDENT"]}><Heading eyebrow="MY QUEUE" title="Track your turn" desc="Your position refreshes automatically while the queue moves."/>
 {t?<div className="queue-card"><div className="queue-top"><div><div className="eyebrow light">YOUR TOKEN</div><strong>{t.display_token}</strong><p>{t.service_name}</p></div><span className="live-pill"><i/> {t.status}</span></div><div className="queue-grid"><div><small>NOW SERVING</small><b>{t.current_serving||"—"}</b></div><div><small>PEOPLE AHEAD</small><b>{t.people_ahead}</b></div><div><small>ESTIMATED WAIT</small><b>{t.estimated_wait_minutes}<em> min</em></b></div><div><small>EXPECTED TURN</small><b>{t.expected_turn?new Date(t.expected_turn).toLocaleTimeString([], {hour:"2-digit",minute:"2-digit"}):"—"}</b></div></div><div className="queue-alert">{t.status==="CALLED"?<><b>🚨 You're next.</b><span>Please proceed to {t.counter?.name||"the service counter"}{t.counter?.number?` · Counter ${t.counter.number}`:""}.</span></>:t.people_ahead<=2?<><b>Your turn is getting close.</b><span>Consider heading toward the service area.</span></>:<><b>Queue is moving.</b><span>We'll update this page as students are served.</span></>}</div><div className="bar"><span style={{width:`${Math.max(7,Math.min(100,100-t.people_ahead*10))}%`}}/></div><div className="queue-bottom"><span>{t.counter?`${t.counter.name} · ${t.counter.location||"Campus"}`:"Counter will be shown when assigned"}</span><button className="cancel" onClick={cancel}>Cancel token</button></div></div>:<div className="empty"><div className="choose-icon"><Icon n="ticket"/></div><h2>No active token</h2><p>Join a service queue to see your live position, wait time and expected turn.</p><Link className="btn primary" to="/services">Find a service</Link></div>}{msg&&<div className="toast">{msg}</div>}</Guard>
}

function History(){
 const [rows,setRows]=useState([]);useEffect(()=>{api.get("/tokens/my-history").then(r=>setRows(r.data.data))},[]);
 return <Guard roles={["STUDENT"]}><Heading eyebrow="HISTORY" title="Queue history" desc="Your completed, skipped and cancelled visits."/><div className="panel table"><div className="table-head"><b>Token</b><b>Service</b><b>Status</b><b>Wait</b></div>{rows.map(x=><div className="table-row" key={x.id}><b>{x.display_token}</b><span>{x.service_name}</span><span className="tag">{x.status}</span><span>{x.estimated_wait_minutes} min</span></div>)}{!rows.length&&<div className="empty small">No queue history yet.</div>}</div></Guard>
}

function Staff(){
 const [q,setQ]=useState([]),[d,setD]=useState({}),[err,setErr]=useState("");
 async function load(){try{setQ((await api.get("/staff/queue")).data.data);setD((await api.get("/staff/dashboard")).data.data)}catch{}}
 useEffect(()=>{load();const i=setInterval(load,3000);return()=>clearInterval(i)},[]);
 async function act(path){setErr("");try{await api.post(path);load()}catch(e){setErr(e.response?.data?.message||"Action failed")}}
 return <Guard roles={["STAFF"]}><Heading eyebrow="STAFF DESK" title="Live queue desk" desc="Call, serve and complete today's assigned queue."/><div className="stats"><Stat icon="users" label="Waiting" value={d.waiting??0} sub="Students waiting"/><Stat icon="check" label="Completed today" value={d.completed_today??0} sub="Services completed"/><Stat icon="service" label="Assigned services" value={d.assigned_services?.length??0} sub="Your assignments"/></div><div className="panel"><div className="panel-title"><div><h3>Today's queue</h3><p>Staff controls determine the queue progression.</p></div><button className="btn primary" onClick={()=>act("/staff/queue/call-next")}>Call next <Icon n="arrow"/></button></div>{err&&<div className="err">{err}</div>}<div className="staff-list">{q.map(x=><div className="staff-row" key={x.id}><div className="staff-token">{x.display_token}</div><div><b>{x.student_name}</b><small>{x.service}</small></div><span className="tag">{x.status}</span><div className="actions">{x.status==="CALLED"&&<button onClick={()=>act(`/staff/tokens/${x.id}/start`)}>Start service</button>}{x.status==="SERVING"&&<><button onClick={()=>act(`/staff/tokens/${x.id}/complete`)}>Complete</button><button className="ghost" onClick={()=>act(`/staff/tokens/${x.id}/skip`)}>Skip</button></>}</div></div>)}{!q.length&&<div className="empty small">No active tokens.</div>}</div></div></Guard>
}

function Admin(){
 const [d,setD]=useState(null),[users,setUsers]=useState([]);
 useEffect(()=>{api.get("/admin/dashboard").then(r=>setD(r.data.data));api.get("/admin/users").then(r=>setUsers(r.data.data))},[]);
 return <Guard roles={["ADMIN"]}><Heading eyebrow="ADMINISTRATION" title="CampusQ overview" desc="Monitor users, queues and service activity."/><div className="stats four">{d&&<><Stat icon="users" label="Students" value={d.students}/><Stat icon="users" label="Staff" value={d.staff}/><Stat icon="service" label="Services" value={d.services}/><Stat icon="ticket" label="Waiting now" value={d.waiting_tokens}/></>}</div><div className="panel table"><div className="panel-title"><div><h3>Users</h3><p>CampusQ accounts and roles.</p></div></div>{users.map(x=><div className="table-row" key={x.id}><b>{x.name}</b><span>{x.email}</span><span className="tag">{x.role}</span><span>{x.is_active?"Active":"Inactive"}</span></div>)}</div></Guard>
}

function App(){return <Routes><Route path="/login" element={<Login/>}/><Route path="/register" element={<Register/>}/><Route path="/" element={<StudentHome/>}/><Route path="/services" element={<Services/>}/><Route path="/token" element={<Token/>}/><Route path="/history" element={<History/>}/><Route path="/staff" element={<Staff/>}/><Route path="/admin" element={<Admin/>}/><Route path="/admin/users" element={<Admin/>}/><Route path="*" element={<Navigate to="/"/>}/></Routes>}
createRoot(document.getElementById("root")).render(<BrowserRouter><App/></BrowserRouter>);
