
    (function(){
      const root=document.getElementById('leo-neural-atlas');
      const box=root.querySelector('.atlas-network');
      const canvas=box.querySelector('canvas');
      const ctx=canvas.getContext('2d');
      const state={glow:.65,density:145,motion:true};
      const skillsLayer=box.querySelector('.atlas-skills');
      const skillMap={
        conveyor:['Computer vision','Camera calibration','Inverse kinematics','Hardware integration'],
        nexa:['OCR / VLM','RAG pipelines','Data engineering','Model evaluation'],
        drone:['Reinforcement learning','MuJoCo','Reward design','Obstacle avoidance'],
        driving:['PPO','CARLA simulation','Motion planning','PID control'],
        vision:['PyTorch','Motion modeling','Temporal attention','Video segmentation'],
        walker:['Mechanism design','Machining','PETG fabrication','PID tuning']
      };
      let expanded=false,skillPoints=[];
      const projects={
        conveyor:{title:'Robotic sorting',detail:'Perception → calibration → physical action',url:'conveyor-sorting/',x:.32,y:.43},
        nexa:{title:'NeXa research',detail:'Documents → expert knowledge → grounded reasoning',url:'nexa-research/',x:.47,y:.20},
        drone:{title:'Drone pathing',detail:'Sensing → learned policies → obstacle avoidance',url:'drone-pathing-rl/',x:.77,y:.36},
        driving:{title:'Autonomous driving',detail:'Route guidance → local planning → vehicle control',url:'autonomous-driving-planner/',x:.69,y:.57},
        vision:{title:'Occlusion recovery',detail:'Visual history → motion models → scene understanding',url:'seeing-through-occlusion/',x:.23,y:.63},
        walker:{title:'Terrain walker',detail:'Mechanism design → fabrication → stable locomotion',url:'terrain-walker/',x:.52,y:.73}
      };
      let selected=null,width=0,height=0,frame=0,visible=true,phase=0,px=0,py=0;
      let selectionMode='pointer',lastInput='keyboard',lastPointerType=null,leaveTimer=0;
      const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      const motionButton=box.querySelector('.atlas-motion');
      if(reduced){motionButton.hidden=true;state.motion=false;}
      motionButton.addEventListener('click',()=>{
        state.motion=!state.motion;
        motionButton.textContent=state.motion?'Pause motion':'Resume motion';
        if(state.motion)start();else{cancelAnimationFrame(frame);frame=0;draw();}
      });
      let seed=197;
      function random(){seed=(seed*16807)%2147483647;return(seed-1)/2147483646;}
      const particles=[];
      for(let i=0;i<190;i++){
        const a=random()*Math.PI*2,r=Math.sqrt(random()),bend=Math.sin(a*3+.6)*.045;
        particles.push({x:.53+Math.cos(a)*(r*.39+bend),y:.43+Math.sin(a)*r*.31,z:random(),p:random()*6.28});
      }
      const edges=[];
      particles.forEach((n,i)=>particles.slice(i+1).forEach((m,j)=>{const d=Math.hypot(n.x-m.x,n.y-m.y);if(d<.145&&random()<.65)edges.push([i,i+j+1,d]);}));
      function resize(){width=box.clientWidth;height=box.clientHeight;if(!width||!height)return;const dpr=Math.min(window.devicePixelRatio||1,2);canvas.width=width*dpr;canvas.height=height*dpr;if(ctx)ctx.setTransform(dpr,0,0,dpr,0,0);if(expanded)layoutSkills();draw();}
      function layoutSkills(){
        const button=box.querySelector('.atlas-node[aria-pressed=true]');
        const br=button.getBoundingClientRect(),rr=box.getBoundingClientRect();
        const cx=br.left-rr.left+br.width/2,cy=br.top-rr.top+br.height/2;
        const radiusX=Math.min(112,width*.27),radiusY=Math.min(78,height*.18);
        const skillsBottom=Math.min(height-110,root.querySelector('.atlas-selection').offsetTop-16);
        const offsets=[[-1,-.72],[.9,-.9],[1,.82],[-.9,.9]];
        const placed=[];skillPoints=[];
        Array.from(skillsLayer.children).forEach((label,i)=>{
          const w=label.offsetWidth,h=label.offsetHeight;
          let x=Math.max(w/2+5,Math.min(width-w/2-5,cx+offsets[i][0]*radiusX));
          let y=Math.max(h/2+12,Math.min(skillsBottom-h/2,cy+offsets[i][1]*radiusY));
          if(width<600){
            x=Math.max(w/2+5,Math.min(width-w/2-5,width*(i%2===0?.25:.75)));
            const direction=cy<height*.4?1:-1;
            const distance=i<2?45:90;
            y=cy+direction*distance;
          }
          for(let attempt=0;attempt<12;attempt++){
            const hit=placed.find(p=>Math.abs(p.x-x)<(p.w+w)/2+8&&Math.abs(p.y-y)<(p.h+h)/2+8);
            const hitsProject=Math.abs(cx-x)<(br.width+w)/2+8&&Math.abs(cy-y)<(br.height+h)/2+8;
            if(!hit&&!hitsProject)break;
            y+=i<2?-h-9:h+9;
            y=Math.max(h/2+8,Math.min(skillsBottom-h/2,y));
          }
          label.style.left=x+'px';label.style.top=y+'px';placed.push({x,y,w,h});skillPoints.push({x,y,cx,cy});
        });
      }
      function revealSkills(){
        expanded=true;box.classList.add('is-expanded');skillsLayer.hidden=false;skillsLayer.replaceChildren();
        skillMap[selected].forEach(skill=>{const label=document.createElement('span');label.className='atlas-skill';label.setAttribute('role','listitem');label.textContent=skill;skillsLayer.appendChild(label);});
        layoutSkills();
      }
      function hideSkills(){
        clearTimeout(leaveTimer);leaveTimer=0;expanded=false;selected=null;
        box.classList.remove('is-expanded');skillsLayer.hidden=true;skillsLayer.replaceChildren();skillPoints=[];
        box.querySelectorAll('.atlas-node').forEach(b=>b.setAttribute('aria-pressed','false'));
        root.querySelector('.atlas-selection strong').textContent='Explore the atlas';
        root.querySelector('.atlas-selection-detail').textContent='Hover, focus, or tap a project to discover its skills.';
        root.querySelector('.atlas-selection-link').hidden=true;
        draw();
      }
      function scheduleDeselect(){
        if(selectionMode==='keyboard'||leaveTimer||!expanded)return;
        leaveTimer=setTimeout(hideSkills,180);
      }
      function insideCluster(x,y){
        const targets=[box.querySelector('.atlas-node[aria-pressed=true]'),...skillsLayer.children,root.querySelector('.atlas-selection-link')];
        const rects=targets.filter(Boolean).map(el=>el.getBoundingClientRect());
        const buffer=32;
        return x>=Math.min(...rects.map(r=>r.left))-buffer&&x<=Math.max(...rects.map(r=>r.right))+buffer&&y>=Math.min(...rects.map(r=>r.top))-buffer&&y<=Math.max(...rects.map(r=>r.bottom))+buffer;
      }
      function draw(){
        if(!ctx)return;
        ctx.clearRect(0,0,width,height);const t=phase;const active=projects[selected]||{x:-10,y:-10};
        const points=particles.map(n=>({x:n.x*width+Math.sin(t+n.p)*2.2+px*n.z*7,y:n.y*height+Math.cos(t*.7+n.p)*2+py*n.z*6,z:n.z}));
        edges.forEach(([i,j,d])=>{if(i>=state.density||j>=state.density)return;const a=points[i],b=points[j];const near=Math.hypot(particles[i].x-active.x,particles[i].y-active.y)<.19;ctx.strokeStyle=near?'rgba(159,200,185,.28)':'rgba(109,151,158,.14)';ctx.lineWidth=near?.7:.5;ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();});
        points.slice(0,state.density).forEach((n,i)=>{const near=Math.hypot(particles[i].x-active.x,particles[i].y-active.y)<.12;ctx.fillStyle=near?'rgba(202,182,146,.8)':`rgba(145,188,185,${.2+n.z*.6})`;ctx.beginPath();ctx.arc(n.x,n.y,.65+n.z*.8,0,Math.PI*2);ctx.fill();});
        const cx=active.x*width-25,cy=active.y*height;const grad=ctx.createRadialGradient(cx,cy,0,cx,cy,65);grad.addColorStop(0,'rgba(169,196,165,.08)');grad.addColorStop(1,'rgba(169,196,165,0)');ctx.fillStyle=grad;ctx.fillRect(cx-65,cy-65,130,130);
        if(expanded){skillPoints.forEach(p=>{ctx.strokeStyle='rgba(158,205,196,.65)';ctx.lineWidth=.85;ctx.beginPath();ctx.moveTo(p.cx,p.cy);ctx.quadraticCurveTo((p.cx+p.x)/2+10,(p.cy+p.y)/2-7,p.x,p.y);ctx.stroke();});}
      }
      function animate(){if(!ctx||!visible||document.hidden||reduced||!state.motion){frame=0;return;}phase+=.0018;draw();frame=requestAnimationFrame(animate);}
      function start(){if(!frame&&visible&&!reduced&&state.motion)frame=requestAnimationFrame(animate);}
      function select(key,mode='pointer'){if(!projects[key])return;clearTimeout(leaveTimer);leaveTimer=0;selectionMode=mode;selected=key;root.querySelectorAll('.atlas-node').forEach(b=>{b.setAttribute('aria-pressed',String(b.dataset.project===key));b.setAttribute('aria-label',projects[b.dataset.project].title+': '+skillMap[b.dataset.project].join(', '));});const p=projects[key];root.querySelector('.atlas-selection strong').textContent=p.title;root.querySelector('.atlas-selection-detail').textContent=p.detail;const link=root.querySelector('.atlas-selection-link');link.href=p.url;link.hidden=false;revealSkills();draw();}
      document.addEventListener('keydown',()=>{lastInput='keyboard';},true);
      document.addEventListener('pointerdown',e=>{
        lastInput='pointer';lastPointerType=e.pointerType;
        if(!e.target.closest('.atlas-node,.atlas-selection,.atlas-motion'))hideSkills();
      },true);
      root.querySelectorAll('.atlas-node').forEach(b=>{
        b.addEventListener('click',e=>{
          const isTouch=e.pointerType==='touch'||lastPointerType==='touch';
          if(e.detail===0||!isTouch){window.location.assign(projects[b.dataset.project].url);return;}
          if(lastPointerType==='touch'&&expanded&&selected===b.dataset.project)hideSkills();
          else select(b.dataset.project);
          lastPointerType=null;
        });
        b.addEventListener('pointerenter',e=>{if(e.pointerType!=='touch')select(b.dataset.project);});
        b.addEventListener('focus',()=>{if(lastInput==='keyboard')select(b.dataset.project,'keyboard');});
      });
      box.addEventListener('pointermove',e=>{
        if(e.pointerType==='touch')return;
        const r=box.getBoundingClientRect();
        if(state.motion&&!reduced){px=(e.clientX-r.left)/r.width-.5;py=(e.clientY-r.top)/r.height-.5;}
        if(expanded&&selectionMode!=='keyboard'){
          if(insideCluster(e.clientX,e.clientY)){clearTimeout(leaveTimer);leaveTimer=0;}else scheduleDeselect();
        }
        if(reduced||!state.motion)draw();
      });
      box.addEventListener('pointerleave',e=>{if(e.pointerType==='touch')return;if(state.motion&&!reduced){px=0;py=0;}scheduleDeselect();draw();});
      box.addEventListener('focusout',e=>{if(!box.contains(e.relatedTarget)&&selectionMode==='keyboard')hideSkills();});
      box.addEventListener('keydown',e=>{if(e.key==='Escape')hideSkills();});
      new ResizeObserver(resize).observe(box);
      new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;if(visible)start();}).observe(box);
      document.addEventListener('visibilitychange',()=>{if(!document.hidden)start();});
      hideSkills();resize();start();
    })();
  
