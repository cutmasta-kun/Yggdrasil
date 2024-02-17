import React from 'react';
import logo from './logo.svg';
import './App.css';

function App() {
  return (
    <div className='w-full h-full bg-teal-300 flex'>
      <div className='h-full w-1/4 bg-slate-100 p-10 flex flex-col'>
        
        <div className='
        cursor-pointer 
        transition 
        duration-150 
        ease-out 
        hover:ease-in 
        border-4 
        border-slate-700 
        h-1/6 
        flex 
        items-center 
        justify-center 
        hover:bg-slate-700 
        text-slate-900 
        hover:text-slate-100
        '>
          <h1 className='text-3xl'>Yggdrasil</h1>
        </div>

        <div className='w-full h-5/6 py-4 flex flex-col'>
          <div className='w-full h-full'>

            <div className='flex flex-row w-full'>
              <div className='
              overflow-hidden 
              hover:bg-slate-700 
              cursor-pointer 
              relative 
              w-3/4 
              text-2xl 
              border-2 
              border-transparent 
              border-b-slate-700 
              transition 
              duration-150 
              ease-out 
              hover:ease-in'>
        
                <div className='
                p-2 
                w-full 
                h-full 
                before:transition-transform 
                before:-translate-x-full 
                before:duration-200 
                hover:before:translate-x-0 
                transition 
                duration-200 
                ease-out 
                hover:ease-in 
                hover:text-slate-100 
                relative 
                bg-transparent 
                before:absolute 
                before:bg-slate-700 
                before:top-0 
                before:left-0 
                before:w-full 
                before:h-full
                '>
                  <span className='py-2 relative'>
                    Memory Interface
                  </span>
                </div>
                
              </div>
              <div className='w-1/4 text-2xl p-2'>
                 
              </div>
            </div>
            <div className='flex flex-row w-full'>
              <div className='
              overflow-hidden 
              hover:bg-slate-700 
              cursor-pointer 
              relative 
              w-3/4 
              text-2xl 
              border-2 
              border-transparent 
              border-b-slate-700 
              transition 
              duration-150 
              ease-out 
              hover:ease-in
              '>
                <div className='
                p-2 
                w-full 
                h-full 
                before:transition-transform 
                before:-translate-x-full 
                before:duration-200 
                hover:before:translate-x-0 
                transition 
                duration-200 
                ease-out 
                hover:ease-in 
                hover:text-slate-100 
                relative 
                bg-transparent 
                before:absolute 
                before:bg-slate-700 
                before:top-0 
                before:left-0 
                before:w-full 
                before:h-full
                '>
                  <span className='py-2 relative'>
                    NTFY
                  </span>
                </div>
                
              </div>
              <div className='w-1/4 text-2xl p-2'>
                 
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className='h-full w-3/4 bg-slate-200 p-10'>

      </div>
    </div>
  );
}

export default App;
